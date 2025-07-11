# 🔐 Secure Receipt OCR with Donut + Gramine

This project runs confidential receipt data extraction using [Donut (CORD)](https://github.com/clovaai/donut) inside a Gramine enclave-like Docker container (no raw data exposure). It parses receipt images into structured JSON using OCR + NER.

Useful link for reference:
([url](https://gramine.readthedocs.io/en/latest/tutorials/pytorch/index.html))
## 📦 Run

```bash
#FIRST...
docker pull ghcr.io/rishabh20399/donut_gramine:latest

#THEN...
#[OPTION 1]
sudo docker run --rm -it --cap-add=SYS_PTRACE --security-opt seccomp=unconfined --entrypoint /bin/bash donut-gramine-final

# OR...

#[OPTION 2]
docker run --rm -it \
  --cap-add=SYS_PTRACE \
  --security-opt seccomp=unconfined \
  -v $(pwd)/receipts:/app/receipts \
  -v $(pwd)/outputs:/app/outputs \
  yourdockerhubusername/donut-gramine \
  bash -c "gramine-direct python3 donut_infer.py"

#FINALLY INSIDE YOUR CONTAINER DO ...
gramine-direct gramine
