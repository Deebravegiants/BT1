# [M] Improper Input Validation in OpenCV

## Summary
Severity: Medium
Advisory: GHSA-fffj-9qwg-qmh5
CVE: CVE-2016-1517
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-fffj-9qwg-qmh5
Type: github-advisory

## Affected
- PyPI: `opencv-python` — affected >=0 <3.3.1.11
- PyPI: `opencv-contrib-python` — affected >=0 <3.3.1.11

## Details
OpenCV 3.0.0 allows remote attackers to cause a denial of service (segfault) via vectors involving corrupt chunks. This issue was fixed in OpenCV version 3.3.1 (corresponding to OpenCV 3.3.1.11).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1517
- https://github.com/opencv/opencv/issues/5956
- https://github.com/opencv/opencv/pull/9376
- https://arxiv.org/pdf/1701.04739.pdf
- https://github.com/opencv/opencv-python
