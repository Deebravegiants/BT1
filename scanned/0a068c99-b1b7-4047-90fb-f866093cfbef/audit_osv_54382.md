# [M] CVE-2023-53900

## Summary
Severity: Medium
Advisory: CVE-2023-53900
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2023-53900
Type: osv

## Details
Spip 4.1.10 contains a file upload vulnerability that allows attackers to upload malicious SVG files with embedded external links. Attackers can trick administrators into clicking a crafted SVG logo that redirects to a potentially dangerous URL through improper file upload filtering.

## References
- https://www.spip.net/en_rubrique25.html
- https://www.vulncheck.com/advisories/spip-admin-account-spoofing-via-malicious-svg-upload
- https://www.exploit-db.com/exploits/51557
