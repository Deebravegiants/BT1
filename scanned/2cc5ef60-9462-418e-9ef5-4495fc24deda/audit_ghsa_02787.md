# [H] Denial of Service in OpenCV

## Summary
Severity: High
Advisory: GHSA-pqjj-6f5q-gqph
CVE: CVE-2017-12602
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-pqjj-6f5q-gqph
Type: github-advisory

## Affected
- PyPI: `opencv-python` — affected >=0 <3.3.1.11
- PyPI: `opencv-contrib-python` — affected >=0 <3.3.1.11

## Details
OpenCV (Open Source Computer Vision Library) through 3.3 (corresponding to OpenCV-Python 3.3.0.9) has a denial of service (memory consumption) issue, as demonstrated by the 10-opencv-dos-memory-exhaust test case.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12602
- https://github.com/opencv/opencv/issues/9311
- https://github.com/opencv/opencv/pull/9376
- https://github.com/opencv/opencv-python
- https://github.com/xiaoqx/pocs/blob/master/opencv.md
- https://security.gentoo.org/glsa/201712-02
