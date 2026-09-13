# [H] Javascript Injection in Vending Info/Buyers Info Module in FluxCP

## Summary
Severity: High
Advisory: CVE-2024-45799
Aliases: GHSA-xvqv-25vf-88g4
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-09-16
Source: https://osv.dev/vulnerability/CVE-2024-45799
Type: osv

## Details
FluxCP is a web-based Control Panel for rAthena servers written in PHP. A javascript injection is possible via venders/buyers list pages and shop names, that are currently not sanitized. This allows executing arbitrary javascript code on the user's browser just by visiting the shop pages. As a result all logged in to fluxcp users can have their session info stolen. This issue has been addressed in release version 1.3. All users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45799.json
- https://github.com/rathena/FluxCP/security/advisories/GHSA-xvqv-25vf-88g4
- https://nvd.nist.gov/vuln/detail/CVE-2024-45799
