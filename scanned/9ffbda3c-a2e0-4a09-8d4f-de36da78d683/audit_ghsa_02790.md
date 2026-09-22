# [M] Divide By Zero in OpenCV.

## Summary
Severity: Medium
Advisory: GHSA-hxfw-jm98-v4mq
CVE: CVE-2019-15939
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-hxfw-jm98-v4mq
Type: github-advisory

## Affected
- PyPI: `opencv-python` — affected >=0 <4.1.1.26
- PyPI: `opencv-python-headless` — affected >=0 <4.1.1.26
- PyPI: `opencv-contrib-python` — affected >=0 <4.1.1.26
- PyPI: `opencv-contrib-python-headless` — affected >=0 <4.1.1.26

## Details
An issue was discovered in OpenCV 4.1.0 (OpenCV-Python 4.1.0.25). There is a divide-by-zero error in cv::HOGDescriptor::getDescriptorSize in modules/objdetect/src/hog.cpp.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15939
- https://github.com/OpenCV/opencv/issues/15287
- https://github.com/opencv/opencv/pull/15382
- https://github.com/opencv/opencv-python
- https://lists.debian.org/debian-lts-announce/2021/10/msg00028.html
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00025.html
