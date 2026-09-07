# [C] Melis Platform CMS Unauthenticated File Upload Leading to RCE

## Summary
Severity: Critical
Advisory: GHSA-chw4-gjvw-3gxc
CVE: CVE-2025-10353
CWE: CWE-43
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-08
Source: https://github.com/advisories/GHSA-chw4-gjvw-3gxc
Type: github-advisory

## Affected
- Packagist: `melisplatform/melis-cms-slider` — affected >=0 <5.3.1

## Details
File upload leading to remote code execution (RCE) in the “melis-cms-slider” module of Melis Technology's Melis Platform. This vulnerability allows an attacker to upload a malicious file via a POST request to '/melis/MelisCmsSlider/MelisCmsSliderDetails/saveDetailsForm' using the 'mcsdetail_img' parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-10353
- https://github.com/melisplatform/melis-cms-slider/commit/c8757338ccd2dae5d347db5f494922ecc692f614
- https://github.com/ivansmc00/CVE-2025-10353-POC
- https://github.com/melisplatform/melis-cms-slider
- https://www.incibe.es/en/incibe-cert/notices/aviso/multiple-vulnerabilities-melis-platform
