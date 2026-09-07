# [M] Reachable Assertion in OpenCV.

## Summary
Severity: Medium
Advisory: GHSA-89rj-5ggj-3p9p
CVE: CVE-2018-5269
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-89rj-5ggj-3p9p
Type: github-advisory

## Affected
- PyPI: `opencv-python` — affected >=0 <3.4.1.15
- PyPI: `opencv-contrib-python` — affected >=0 <3.4.1.15

## Details
In OpenCV 3.3.1 (corresponds with OpenCV-Python 3.3.1.11), an assertion failure happens in cv::RBaseStream::setPos in modules/imgcodecs/src/bitstrm.cpp because of an incorrect integer cast.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-5269
- https://github.com/opencv/opencv/issues/10540
- https://github.com/opencv/opencv/pull/10563
- https://github.com/opencv/opencv-python
- https://lists.debian.org/debian-lts-announce/2018/04/msg00019.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00030.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00028.html
- http://www.securityfocus.com/bid/106945
