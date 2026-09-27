# [H] Denial of Service in OpenCV

## Summary
Severity: High
Advisory: GHSA-fr58-2xhv-qp3w
CVE: CVE-2017-12600
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-fr58-2xhv-qp3w
Type: github-advisory

## Affected
- PyPI: `opencv-python` — affected >=0 <3.3.1.11
- PyPI: `opencv-contrib-python` — affected >=0 <3.3.1.11

## Details
OpenCV (Open Source Computer Vision Library) through 3.3 (corresponding to OpenCV-Python 3.3.0.9) has a denial of service (CPU consumption) issue, as demonstrated by the 11-opencv-dos-cpu-exhaust test case.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12600
- https://github.com/opencv/opencv/issues/9311
- https://github.com/opencv/opencv/pull/9376
- https://github.com/opencv/opencv-python
- https://github.com/opencv/opencv-python/releases/tag/11
- https://github.com/opencv/opencv-python/releases/tag/9
- https://github.com/xiaoqx/pocs/blob/master/opencv.md
- https://security.gentoo.org/glsa/201712-02
