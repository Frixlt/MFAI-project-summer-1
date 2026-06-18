# Copyright (C) 2015-2020 Danilo Bargen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
Generate coverage badges for Coverage.py.
"""

import argparse
from pathlib import Path
import sys

try:
    import coverage
except ImportError:
    coverage = None


__version__ = "1.1.2"
__all__ = ()


DEFAULT_COLOR = "#a4a61d"
COLORS = {
    "brightgreen": "#4c1",
    "green": "#97CA00",
    "yellowgreen": "#a4a61d",
    "yellow": "#dfb317",
    "orange": "#fe7d37",
    "red": "#e05d44",
    "lightgrey": "#9f9f9f",
}

COLOR_RANGES = [
    (95, "brightgreen"),
    (90, "green"),
    (75, "yellowgreen"),
    (60, "yellow"),
    (40, "orange"),
    (0, "red"),
]


class Devnull:
    """
    A file like object that does nothing.
    """

    def write(self, *args, **kwargs):
        pass


def get_total():
    """
    Return the rounded total as properly rounded string.
    """
    cov = coverage.Coverage()
    cov.load()
    total = cov.report(file=Devnull())

    if hasattr(coverage.results.Numbers, "set_precision"):  # Coverage <= 5

        class Precision(coverage.results.Numbers):
            """
            A class for using the percentage rounding of the main coverage package,
            with any percentage.

            To get the string format of the percentage, use the ``pc_covered_str``
            property.

            """

            def __init__(self, percent):
                self.percent = percent

            @property
            def pc_covered(self):
                return self.percent

        return Precision(total).pc_covered_str

    if hasattr(coverage.results.Numbers, "display_covered"):  # Coverage 6.x < 7.5
        # NOTE: Precision is no longer set globally in the
        # `coverage.results.Numbers` class. Instead the precision must be
        # passed in as the first argument. We pull the precision from the
        # `coverage.Coverage` object because it should pull the correct
        # precision from the local .coveragerc file.
        return coverage.results.Numbers(precision=cov.config.precision).display_covered(total)

    # For Coverage >= 7.5
    return coverage.results.display_covered(total, cov.config.precision)


def get_color(total):
    """
    Return color for current coverage precent
    """
    try:
        xtotal = int(total)
    except ValueError:
        return COLORS["lightgrey"]
    for range_, color in COLOR_RANGES:
        if xtotal >= range_:
            return COLORS[color]
    return COLORS["lightgrey"]


def get_badge(total, color=DEFAULT_COLOR):
    """
    Read the SVG template from the package, update total, return SVG as a
    string.
    """
    template_path = Path(__file__).parent / "templates" / "flat.svg"
    template = template_path.read_text(encoding="utf-8")
    return template.replace("{{ total }}", total).replace("{{ color }}", color)


def parse_args(argv=None):
    """
    Parse the command line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", dest="filepath", help="Save the file to the specified path.")
    parser.add_argument(
        "-p",
        dest="plain_color",
        action="store_true",
        help="Plain color mode. Standard green badge.",
    )
    parser.add_argument(
        "-f", dest="force", action="store_true", help="Force overwrite image, use with -o key."
    )
    parser.add_argument(
        "-q", dest="quiet", action="store_true", help="Don't output any non-error messages."
    )
    parser.add_argument("-v", dest="print_version", action="store_true", help="Show version.")

    # If arguments have been passed in, use them.
    if argv:
        return parser.parse_args(argv)

    # Otherwise, just use sys.argv directly.
    return parser.parse_args()


def save_badge(badge, filepath, force=False):
    """
    Save badge to the specified path.
    """
    # Validate path (part 1)
    if filepath.endswith("/"):
        sys.stderr.write("Error: Filepath may not be a directory.\n")
        sys.exit(1)

    # Get absolute filepath
    path = Path(filepath).resolve()
    if path.suffix.lower() != ".svg":
        path = path.with_suffix(".svg")

    # Validate path (part 2)
    if not force and path.exists():
        sys.stderr.write(f'Error: "{path}" already exists.\n')
        sys.exit(1)

    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    path.write_text(badge, encoding="utf-8")

    return str(path)


def main(argv=None):
    """
    Console scripts entry point.
    """
    args = parse_args(argv)

    # Print version
    if args.print_version:
        sys.stdout.write(f"coverage-badge v{__version__}\n")
        sys.exit(0)

    # Check for coverage
    if coverage is None:
        sys.stderr.write("Error: Python coverage module not installed.\n")
        sys.exit(1)

    # Generate badge
    try:
        total = get_total()
    except coverage.misc.CoverageException as e:
        sys.stderr.write(f"Error: {e} Did you run coverage first?\n")
        sys.exit(1)

    color = DEFAULT_COLOR if args.plain_color else get_color(total)
    badge = get_badge(total, color)

    # Show or save output
    if args.filepath:
        path = save_badge(badge, args.filepath, args.force)
        if not args.quiet:
            sys.stdout.write(f"Saved badge to {path}\n")
    else:
        sys.stdout.write(badge)


if __name__ == "__main__":
    main()
