# [H] Double Free in OpenCV

## Summary
Severity: High
Advisory: GHSA-cvhw-2593-5j2q
CVE: CVE-2016-1516
CWE: CWE-415
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-cvhw-2593-5j2q
Type: github-advisory

## Affected
- PyPI: `opencv-python` — affected >=0 <3.3.1.11
- PyPI: `opencv-contrib-python` — affected >=0 <3.3.1.11

## Details
OpenCV 3.0.0 has a double free issue that allows attackers to execute arbitrary code. This issue was fixed in OpenCV version 3.3.1 (corresponding to OpenCV-Python and and OpenCV-Contrib-Python 3.3.1.11).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1516
- https://github.com/opencv/opencv/issues/5956
- https://github.com/opencv/opencv/pull/9376
- https://arxiv.org/pdf/1701.04739.pdf
- https://github.com/opencv/opencv-python
- https://lists.debian.org/debian-lts-announce/2018/07/msg00030.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00028.html
