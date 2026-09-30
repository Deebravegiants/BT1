# [H] Out-of-bounds Write in OpenCV

## Summary
Severity: High
Advisory: GHSA-q799-q27x-vp7w
CVE: CVE-2019-5064
CWE: CWE-120, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-q799-q27x-vp7w
Type: github-advisory

## Affected
- PyPI: `opencv-python` — affected >=0 <4.2.0.32
- PyPI: `opencv-python-headless` — affected >=0 <4.2.0.32
- PyPI: `opencv-contrib-python` — affected >=0 <4.2.0.32
- PyPI: `opencv-contrib-python-headless` — affected >=0 <4.2.0.32

## Details
An exploitable heap buffer overflow vulnerability exists in the data structure persistence functionality of OpenCV, version 4.1.0 (corresponds with OpenCV-Python version 4.1.2.30). A specially crafted JSON file can cause a buffer overflow, resulting in multiple heap corruptions and potentially code execution. An attacker can provide a specially crafted file to trigger this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5064
- https://github.com/opencv/opencv/issues/15857
- https://github.com/opencv/opencv-python
- https://github.com/opencv/opencv-python/releases/tag/32
- https://github.com/opencv/opencv/releases/tag/4.2.0
- https://talosintelligence.com/vulnerability_reports/TALOS-2019-0853
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
