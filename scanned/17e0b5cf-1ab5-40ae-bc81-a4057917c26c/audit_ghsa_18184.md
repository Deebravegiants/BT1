# [M] Ghost vulnerable to Server Side Request Forgery (SSRF) via oEmbed Bookmark

## Summary
Severity: Medium
Advisory: GHSA-f7qg-xj45-w956
CVE: CVE-2025-9862
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-f7qg-xj45-w956
Type: github-advisory

## Affected
- npm: `ghost` — affected >=6.0.0 <6.0.9
- npm: `ghost` — affected >=5.99.0 <5.130.4

## Details
### Impact

A vulnerability in Ghost's oEmbed mechanism allows staff users to exfiltrate data from internal systems via SSRF.

### Vulnerable versions

This vulnerability is present in Ghost v5.99.0 to v5.130.3 to and Ghost v6.0.0 to v6.0.8.

### Patches

v5.130.4 and v6.0.9 contain a fix for this issue.

### References

The original report is available here: https://fluidattacks.com/advisories/regida

We thank Cristian Vargas for discovering and disclosing this vulnerability responsibly. 

### For more information

If you have any questions or comments about this advisory, email us at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-f7qg-xj45-w956
- https://nvd.nist.gov/vuln/detail/CVE-2025-9862
- https://github.com/TryGhost/Ghost/commit/01d64c7c0ffbf90cd036195c60ded6d08077d612
- https://github.com/TryGhost/Ghost/commit/ffe9d079afa68557c581d224f1ff126e625b06e3
- https://fluidattacks.com/advisories/regida
- https://github.com/TryGhost/Ghost
- https://github.com/TryGhost/Ghost/releases/tag/v6.0.9
