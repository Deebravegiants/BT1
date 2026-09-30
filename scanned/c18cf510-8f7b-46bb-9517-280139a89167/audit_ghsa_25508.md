# [M] Manipulated inline images can cause Infinite Loop in PyPDF2

## Summary
Severity: Medium
Advisory: GHSA-xcjx-m2pj-8g79
CVE: CVE-2022-24859
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-xcjx-m2pj-8g79
Type: github-advisory

## Affected
- PyPI: `PyPDF2` — affected >=0 <1.27.5

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to an infinite loop if the PyPDF2 user wrote the following code:

```python
from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.pdf import ContentStream

reader = PdfFileReader("malicious.pdf", strict=False)
for page in reader.pages:
    ContentStream(page.getContents(), reader)
```

### Patches

[`PyPDF2==1.27.5`](https://pypi.org/project/PyPDF2) and later are patched.

Credits to [Sebastian Krause](https://github.com/sekrause) for finding ([issue](https://github.com/py-pdf/PyPDF2/issues/329)) and fixing ([PR](https://github.com/py-pdf/PyPDF2/pull/740)) it.

## References
- https://github.com/py-pdf/PyPDF2/security/advisories/GHSA-xcjx-m2pj-8g79
- https://nvd.nist.gov/vuln/detail/CVE-2022-24859
- https://github.com/py-pdf/PyPDF2/issues/329
- https://github.com/py-pdf/PyPDF2/pull/740
- https://github.com/py-pdf/PyPDF2
- https://github.com/py-pdf/PyPDF2/releases/tag/1.27.5
- https://github.com/pypa/advisory-database/tree/main/vulns/pypdf2/PYSEC-2022-194.yaml
- https://lists.debian.org/debian-lts-announce/2022/06/msg00001.html
- https://lists.debian.org/debian-lts-announce/2023/06/msg00013.html
