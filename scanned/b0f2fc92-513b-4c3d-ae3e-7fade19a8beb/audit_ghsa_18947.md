# [M] AstrBot has an arbitrary file read vulnerability in function _encode_image_bs64

## Summary
Severity: Medium
Advisory: GHSA-vm2f-46xc-5jc3
CVE: CVE-2025-57697
CWE: CWE-125, CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-11-07
Source: https://github.com/advisories/GHSA-vm2f-46xc-5jc3
Type: github-advisory

## Affected
- PyPI: `AstrBot` — affected >=0

## Details
AstrBot Project v3.5.22 has an arbitrary file read vulnerability in function _encode_image_bs64. Since the _encode_image_bs64 function defined in entities.py opens the image specified by the user in the request body and returns the image content as a base64-encoded string without checking the legitimacy of the image path, attackers can construct a series of malicious URLs to read any specified file, resulting in sensitive data leakage.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-57697
- https://github.com/AstrBotDevs/AstrBot
- https://github.com/DYX217/vulnerability-explore/blob/main/1/README.md
