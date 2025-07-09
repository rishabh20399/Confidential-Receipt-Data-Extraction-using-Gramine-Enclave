FROM gramineproject/gramine:stable-noble

# Set UTF-8 encoding (avoids tokenizer issues)
ENV LANG=C.UTF-8

# Install system dependencies
RUN apt update && \
    apt install -y python3 python3-pip git libglib2.0-0 gramine

# Create working directory
WORKDIR /app

# Copy local files into container
COPY . .

# Install Python packages
RUN pip3 install --break-system-packages --no-cache-dir \
    torch torchvision torchaudio \
    transformers \
    opencv-python Pillow \
    sentencepiece protobuf \
    beautifulsoup4

# Download and save Donut model (model and processor separately for easier debugging)
RUN python3 -c "\
from transformers import VisionEncoderDecoderModel; \
model = VisionEncoderDecoderModel.from_pretrained('naver-clova-ix/donut-base-finetuned-cord-v2'); \
model.save_pretrained('./donut-cord-model')"

RUN python3 -c "\
from transformers import DonutProcessor; \
processor = DonutProcessor.from_pretrained('naver-clova-ix/donut-base-finetuned-cord-v2'); \
processor.save_pretrained('./donut-cord-model')"

# Build and sign Gramine manifest
#RUN gramine-manifest -Dlog_level=debug gramine.manifest.template.toml > gramine.manifest   
RUN gramine-manifest -Dlog_level=debug gramine.manifest.template.toml > python3.manifest

# Run with Gramine Direct
ENTRYPOINT ["/usr/bin/gramine-direct", "python3", "donut_infer.py"]
