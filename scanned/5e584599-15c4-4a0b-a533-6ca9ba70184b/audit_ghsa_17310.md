# [H] nbconvert has an uncontrolled search path that leads to unauthorized code execution on Windows

## Summary
Severity: High
Advisory: GHSA-xm59-rqc7-hhvf
CVE: CVE-2025-53000
CWE: CWE-427
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-18
Source: https://github.com/advisories/GHSA-xm59-rqc7-hhvf
Type: github-advisory

## Affected
- PyPI: `nbconvert` — affected >=0 <7.17.0

## Details
### Summary

On Windows, converting a notebook containing SVG output to a PDF results in unauthorized code execution. Specifically, a third party can create a `inkscape.bat` file that defines a [Windows batch script](https://en.wikipedia.org/wiki/Batch_file), capable of arbitrary code execution.

When a user runs `jupyter nbconvert --to pdf` on a notebook containing SVG output to a PDF on a Windows platform from this directory, the `inkscape.bat` file is run unexpectedly.

### Details
_Give all details on the vulnerability. Pointing to the incriminated source code is very helpful for the maintainer._

`nbconvert` searches for an `inkscape` executable when converting notebooks to PDFs here: https://github.com/jupyter/nbconvert/blob/4f61702f5c7524d8a3c4ac0d5fc33a6ac2fa36a7/nbconvert/preprocessors/svg2pdf.py#L104

The MITRE page on [CWE-427 (Uncontrolled Search Path Element)](https://cwe.mitre.org/data/definitions/427.html) summarizes the root cause succinctly:

> In Windows-based systems, when the `LoadLibrary` or `LoadLibraryEx` function is called with a DLL name that does not contain a fully qualified path, the function follows a search order that includes two path elements that might be uncontrolled:
> - the directory from which the program has been loaded
> - the current working directory

### PoC

_Complete instructions, including specific configuration details, to reproduce the vulnerability._

1. Create a directory containing: 

    - A hidden bat file called `inkscape.bat` containing `msg * "You've been hacked!"`

    - A dummy ipynb file called `Machine_Learning.ipynb`

2. Run the command `jupyter nbconvert --to pdf Machine_Learning.ipynb`.

3. Wait a few seconds, and you should see a popup showing the message "You've been hacked!" 

### Impact

All Windows users.

## References
- https://github.com/jupyter/nbconvert/security/advisories/GHSA-xm59-rqc7-hhvf
- https://nvd.nist.gov/vuln/detail/CVE-2025-53000
- https://github.com/jupyter/nbconvert/issues/2258
- https://github.com/jupyter/nbconvert/commit/c9ac1d1040459ed1ff9eb34e9918ce5a87cf9d71
- https://github.com/jupyter/nbconvert
- https://github.com/jupyter/nbconvert/blob/4f61702f5c7524d8a3c4ac0d5fc33a6ac2fa36a7/nbconvert/preprocessors/svg2pdf.py#L104
- https://github.com/jupyter/nbconvert/releases/tag/v7.17.0
- https://www.imperva.com/blog/code-execution-in-jupyter-notebook-exports
