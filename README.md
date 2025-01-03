# AWS Whitepapers Downloader

A Python script to download AWS whitepapers from the official AWS documentation site.


## Installation

1. Clone the repository:
```bash
git clone https://github.com/KasteM34/aws-whitepapers-downloader.git
````

2. Get into your virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip3 install -r requirements.txt
```

4. Run it

```bash
python3 downloader.py
```

## Configuration
Edit the constants at the top of downloader.py to customize:

- Download directory
- Page load delay
- Target URL

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.