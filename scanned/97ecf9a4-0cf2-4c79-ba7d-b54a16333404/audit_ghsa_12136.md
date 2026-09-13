# [H] Ghost Vulnerable to Remote Code Execution via Malicious Themes

## Summary
Severity: High
Advisory: GHSA-cgc2-rcrh-qr5x
CVE: CVE-2026-29053
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-cgc2-rcrh-qr5x
Type: github-advisory

## Affected
- npm: `ghost` — affected >=0.7.2 <6.19.1

## Details
### Impact

Specifically crafted malicious themes can execute arbitrary code on the server running Ghost. 

### Vulnerable Versions

This vulnerability is present in Ghost v0.7.2 to v6.19.0.

### Patches

v6.19.1 contains a fix for this issue.

### Workarounds

Ghost generally recommends users refrain from installing untrusted themes. If a malicious theme has already been installed, it is recommended to uninstall the theme and then inspect it to understand its impact, which will be attack-specific. 

### References
Ghost thanks Cristian-Alexandru Staicu at Endor Labs for disclosing this vulnerability responsibly. 

### For more information

If there are any questions or comments about this advisory, email Ghost at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-cgc2-rcrh-qr5x
- https://nvd.nist.gov/vuln/detail/CVE-2026-29053
- https://github.com/TryGhost/Ghost
