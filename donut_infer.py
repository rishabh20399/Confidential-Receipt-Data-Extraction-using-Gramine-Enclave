#from PIL import Image
#from transformers import VisionEncoderDecoderModel, DonutProcessor
#import torch

#device = "cpu"
#model = VisionEncoderDecoderModel.from_pretrained("donut-cord-model").to(device)
#processor = DonutProcessor.from_pretrained("donut-cord-model")

#image = Image.open("receipt.jpg").convert("RGB")
#pixel_values = processor(image, return_tensors="pt").pixel_values.to(device)
#decoder_input_ids = processor.tokenizer("<s_cord-v2>", add_special_tokens=False, return_tensors="pt").input_ids.to(device)

#outputs = model.generate(pixel_values, decoder_input_ids=decoder_input_ids, max_length=512)
#result = processor.batch_decode(outputs, skip_special_tokens=True)[0]
#print(result)

from PIL import Image
from transformers import VisionEncoderDecoderModel, DonutProcessor
from collections import defaultdict
from bs4 import BeautifulSoup
import torch
import os
import json

device = "cpu"

# Load model and processor
model = VisionEncoderDecoderModel.from_pretrained("donut-cord-model").to(device)
processor = DonutProcessor.from_pretrained("donut-cord-model")

# Directory paths
input_dir = "/app/receipts"
output_dir = "/app/outputs"

# Make sure output dir exists
os.makedirs(output_dir, exist_ok=True)

# Define XML to JSON parser
def donut_xml_to_json(xml_string):
    wrapped_xml = f"<root>{xml_string}</root>"
    soup = BeautifulSoup(wrapped_xml, "html.parser")
    data = {}

    for section in soup.root.find_all(recursive=False):
        section_name = section.name
        section_data = defaultdict(list)

        for field in section.find_all(recursive=False):
            section_data[field.name].append(field.text.strip())

        # Simplify lists with single values
        section_data = {
            k: v[0] if len(v) == 1 else v
            for k, v in section_data.items()
        }

        data[section_name] = section_data

    return data

# Process all receipt images
for filename in os.listdir(input_dir):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        image_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename.rsplit(".", 1)[0] + ".json")

        try:
            image = Image.open(image_path).convert("RGB")
            pixel_values = processor(image, return_tensors="pt").pixel_values.to(device)

            decoder_input_ids = processor.tokenizer("<s_cord-v2>", add_special_tokens=False, return_tensors="pt").input_ids.to(device)

            outputs = model.generate(pixel_values, decoder_input_ids=decoder_input_ids)
            result = processor.batch_decode(outputs, skip_special_tokens=True)[0]

            try:
                parsed_json = donut_xml_to_json(result)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(parsed_json, f, indent=4, ensure_ascii=False)
                print(f"✅ Saved structured JSON: {output_path}")
            except Exception as e:
                print(f"❌ Failed to parse pseudo-XML for {filename}: {e}")
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump({"raw_output": result}, f, indent=4, ensure_ascii=False)

        except Exception as e:
            print(f"❌ Failed to process image {filename}: {e}")
