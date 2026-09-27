# [H] NULL Pointer Dereference in OpenCV.

## Summary
Severity: High
Advisory: GHSA-3448-vrgh-85xr
CVE: CVE-2019-14493
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-3448-vrgh-85xr
Type: github-advisory

## Affected
- PyPI: `opencv-python` — affected >=0 <4.1.1.26
- PyPI: `opencv-python-headless` — affected >=0 <4.1.1.26
- PyPI: `opencv-contrib-python` — affected >=0 <4.1.1.26
- PyPI: `opencv-contrib-python-headless` — affected >=0 <4.1.1.26

## Details
An issue was discovered in OpenCV before 4.1.1 (OpenCV-Python before 4.1.1.26). There is a NULL pointer dereference in the function cv::XMLParser::parse at modules/core/src/persistence.cpp.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14493
- https://github.com/opencv/opencv/issues/15127
- https://github.com/opencv/opencv-python
- https://github.com/opencv/opencv/compare/371bba8...ddbd10c
- https://lists.debian.org/debian-lts-announce/2021/10/msg00028.html
