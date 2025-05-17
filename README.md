
# 🔍 Advanced Phone Number OSINT Tool

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Dependencies](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green)

Professional OSINT tool for phone number intelligence gathering with advanced features and rich terminal interface.


## Features

- 📟 Basic Number Analysis (Carrier, Location, Timezone)
- 🔎 Social Media Platform Detection (WhatsApp, Facebook, Telegram)
- 🛡️ Data Breach Check via HIBP API
- 🌐 Google Dorking Integration
- 📊 Rich Terminal Visualization (Tables, Panels, Progress Bars)
- 📁 JSON Export Capability
- 🕵️ Reverse Lookup Simulation
- 🔗 Direct Browser Integration

## Repository Structure

```text
phone-osint/
├── main.py              
├── requirements.txt   
└── README.md
```

## System Requirements

- Python 3.8+
- pip 20.0+
- Terminal with UTF-8 support

## Installation & Setup

1. **Clone Repository**
```bash
git clone https://github.com/FreedomSec1337/CentTR
cd CentTR
```

2. **Create Virtual Environment**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/MacOS
.venv\Scripts\activate     # Windows
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

## Usage

```bash
python3 main.py
```

Example workflow:
1. Enter phone number in international format (+[country code][number])
2. Provide HIBP API key when prompted (optional)
3. View interactive results
4. Choose to save results or open links

## Configuration

Create `.env` file for API keys:
```env
HIBP_API_KEY=your_api_key_here
```

## Dependencies List (requirements.txt)

```text
phonenumbers==8.13.22
requests==2.31.0
googlesearch-python==1.2.3
rich==13.7.0
pyfiglet==1.0.2
```

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## Disclaimer

❗ This tool is intended for **legal and ethical use only**. Always verify your local laws and target platform's Terms of Service before conducting any OSINT investigations.

