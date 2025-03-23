# Estradiol Simulator

## Overview

The Estradiol Simulator is a web application designed to perform pharmacokinetic calculations for injectable estradiol. It provides an interactive interface for users to input various parameters related to estradiol administration and visualize the resulting hormone levels over time using Plotly.

## Features

- User-friendly web interface for inputting pharmacokinetic parameters.
- Real-time updates of estradiol levels plotted on a graph.
- AJAX functionality for seamless interaction without page reloads.
- Modern design that complements the visualizations.

## Project Structure

```text
estradiol-simulator
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── pharmacokinetics.py
├── static
│   ├── css
│   │   └── styles.css
│   ├── favicon
│   │   ├── favicon.ico, +variations
│   │   └── site.webmanifest
│   └── js
│       └── app.js
├── templates
│   └── index.html
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## Installation

1. Clone the repository:

   ```text
   git clone <repository-url>
   cd estradiol-simulator
   ```

2. Create a virtual environment (optional but recommended):

   ```text
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:

   ```text
   pip install -r requirements.txt
   ```

## Usage

1. Start the FastAPI application:

   ```text
   uvicorn app.main:app --reload
   ```

2. Open your web browser and navigate to `http://127.0.0.1:8000`.

3. Input the desired parameters for estradiol administration and observe the resulting pharmacokinetic plot.

## Dependencies

The project requires the following Python packages:

- FastAPI
- Uvicorn
- Plotly
- NumPy
- Jinja2
- Any other necessary libraries listed in `requirements.txt`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
