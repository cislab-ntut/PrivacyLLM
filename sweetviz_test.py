"""Sweetviz comparison report generator

This script creates an interactive Sweetviz HTML report that compares two CSV
files. Typical usage from the command line:

    pip install sweetviz pandas
    python sweetviz_test.py --input1 ori_214000_float.csv \
                            --input2 ori_214000_ver_syn_float.csv \
                            --output sweetviz_report.html

Open the generated `sweetviz_report.html` in your browser to explore the data.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd
import sweetviz as sv


def generate_report(input1: Path | str, input2: Path | str, output: Path | str = "sweetviz_report.html") -> None:
    """Generate a Sweetviz comparison report for *input1* vs *input2*.

    Parameters
    ----------
    input1, input2 : Path | str
        Paths to the two CSV files you want to compare.
    output : Path | str, default "sweetviz_report.html"
        Where to write the HTML report.
    """
    input1 = Path(input1)
    input2 = Path(input2)
    output = Path(output)

    # Read the datasets
    df1 = pd.read_csv(input1)
    df2 = pd.read_csv(input2)

    # Build and generate the report
    report = sv.compare([df1, "Original"], [df2, "Synthetic"], target_feat=None)
    report.show_html(str(output), open_browser=False)
    print(f"\nSweetviz report created: {output.resolve()}\nOpen it in your browser to explore the results.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a Sweetviz comparison report between two CSV datasets.")
    parser.add_argument("--input1", required=True, help="Path to the first CSV file (baseline dataset)")
    parser.add_argument("--input2", required=True, help="Path to the second CSV file (dataset to compare)")
    parser.add_argument("--output", default="sweetviz_report.html", help="Name/path for the output HTML report")

    args = parser.parse_args()
    generate_report(args.input1, args.input2, args.output)


if __name__ == "__main__":
    main()
