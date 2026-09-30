# [H] python-libarchive directory traversal

## Summary
Severity: High
Advisory: GHSA-75mx-hw5q-pvx3
CVE: CVE-2024-55587
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-12-12
Source: https://github.com/advisories/GHSA-75mx-hw5q-pvx3
Type: github-advisory

## Affected
- PyPI: `python-libarchive` — affected >=0

## Details
python-libarchive through 4.2.1 allows directory traversal (to create files) in extract in zip.py for ZipFile.extractall and ZipFile.extract.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-55587
- https://github.com/smartfile/python-libarchive/issues/42
- https://github.com/smartfile/python-libarchive/pull/41
- https://github.com/smartfile/python-libarchive
- https://github.com/smartfile/python-libarchive/blob/c7677411bfc4ab5701d343bc6ebd9e35c990e80e/libarchive/zip.py#L107
