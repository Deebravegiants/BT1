# [H] raspap-webgui has a Directory Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-277f-37gw-9gmq
CVE: CVE-2025-44163
CWE: CWE-22, CWE-23
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-06-27
Source: https://github.com/advisories/GHSA-277f-37gw-9gmq
Type: github-advisory

## Affected
- Packagist: `billz/raspap-webgui` — affected >=0 <3.3.6

## Details
RaspAP raspap-webgui 3.3.1 is vulnerable to Directory Traversal in ajax/networking/get_wgkey.php. An authenticated attacker can send a crafted POST request with a path traversal payload in the `entity` parameter to overwrite arbitrary files writable by the web server via abuse of the `tee` command used in shell execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-44163
- https://github.com/RaspAP/raspap-webgui/commit/eb53c46c336384d78336b021adea94d9257e1d67
- https://gist.github.com/YichaoXu/3694f039a3d1b973efd068e4dc662a41
- https://github.com/RaspAP/raspap-webgui
- https://github.com/RaspAP/raspap-webgui/blob/125ae7a39ad7c9a71250d3b3e349fd767687ff8d/ajax/networking/get_wgkey.php#L9
