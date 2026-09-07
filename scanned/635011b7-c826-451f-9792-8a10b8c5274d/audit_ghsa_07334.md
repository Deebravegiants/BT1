# [H] vantage6: Algorithm developer can edit another developer's algorithm that is pending / under review

## Summary
Severity: High
Advisory: GHSA-47w6-gwp4-w6vc
CVE: CVE-2026-73652
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-47w6-gwp4-w6vc
Type: github-advisory

## Affected
- PyPI: `vantage6` — affected >=0

## Details
### Impact
Edit permission lacks ownership check, so another developer could alter metadata that is later trusted by nodes. 

Worst they could do is update the image or image tag. If that is not noted, another image is approved than the one actually under review

### Patches
No

### Workarounds
No

## References
- https://github.com/vantage6/vantage6/security/advisories/GHSA-47w6-gwp4-w6vc
- https://github.com/vantage6/vantage6
