# Dialogue Observe

A Python project for dialogue creation and critque via locally hosted language models.

## Setup

### Prerequisites
- Python 3.13 or higher
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd dialogue_observe
```

2. Create and activate a virtual environment:
```bash
python -m venv dialogue_env
source dialogue_env/bin/activate  # On Windows: dialogue_env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main script:
```bash
python base.py
```

## Project Structure

```
dialogue_observe/
├── base.py              # Main application file
├── dialogue_env/        # Virtual environment (ignored by git)
├── .gitignore          # Git ignore patterns
└── README.md           # This file
```

## Development

### Setting up for Development

1. Follow the installation steps above
2. Install development dependencies (if any):
```bash
pip install -r requirements-dev.txt
```

### Running Tests

```bash
python -m pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

