# [H] Integer Overflow or Wraparound in OpenCV.

## Summary
Severity: High
Advisory: GHSA-m43c-649m-pm48
CVE: CVE-2017-1000450
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-m43c-649m-pm48
Type: github-advisory

## Affected
- PyPI: `opencv-python` — affected >=0 <3.3.1.11
- PyPI: `opencv-contrib-python` — affected >=0 <3.3.1.11

## Details
In opencv/modules/imgcodecs/src/utils.cpp, functions FillUniColor and FillUniGray do not check the input length, which can lead to integer overflow. If the image is from remote, may lead to remote code execution or denial of service. This affects Opencv 3.3 (corresponding with OpenCV-Python 3.3.0.9) and earlier.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000450
- https://github.com/opencv/opencv/issues/9723
- https://github.com/opencv/opencv/pull/9726/commits/c58152d94ba878b2d7d76bcac59146312199b9eb
- https://github.com/blendin/pocs/blob/master/opencv/0.OOB_Write_FillUniColor
- https://github.com/opencv/opencv-python
- https://lists.debian.org/debian-lts-announce/2018/01/msg00008.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00030.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00028.html
