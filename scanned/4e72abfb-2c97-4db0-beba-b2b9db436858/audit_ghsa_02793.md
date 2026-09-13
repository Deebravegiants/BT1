# [M] Out-of-bounds Read in OpenCV

## Summary
Severity: Medium
Advisory: GHSA-x3rm-644h-67m8
CVE: CVE-2019-16249
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-x3rm-644h-67m8
Type: github-advisory

## Affected
- PyPI: `opencv-python` — affected >=0 <4.1.2.30
- PyPI: `opencv-python-headless` — affected >=0 <4.1.2.30
- PyPI: `opencv-contrib-python` — affected >=0 <4.1.2.30
- PyPI: `opencv-contrib-python-headless` — affected >=0 <4.1.2.30

## Details
OpenCV 4.1.1 has an out-of-bounds read in hal_baseline::v_load in core/hal/intrin_sse.hpp when called from computeSSDMeanNorm in modules/video/src/dis_flow.cpp.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16249
- https://github.com/opencv/opencv/issues/15481
- https://github.com/opencv/opencv/pull/15531
- https://bugzilla.redhat.com/show_bug.cgi?id=1752702
- https://github.com/opencv/opencv-python
- https://github.com/opencv/opencv-python/releases/tag/30
