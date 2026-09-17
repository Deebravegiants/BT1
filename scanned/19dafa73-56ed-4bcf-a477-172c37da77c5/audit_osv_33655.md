# [H] Radashi Vulnerable to Improperly Controlled Modification of Object Prototype Attributes ('Prototype Pollution')

## Summary
Severity: High
Advisory: CVE-2025-48054
Aliases: GHSA-2xv9-ghh9-xc69
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2025-05-27
Source: https://osv.dev/vulnerability/CVE-2025-48054
Type: osv

## Details
Radashi is a TypeScript utility toolkit. Prior to version 12.5.1, the set function within the Radashi library is vulnerable to prototype pollution. If an attacker can control parts of the path argument to the set function, they could potentially modify the prototype of all objects in the JavaScript runtime, leading to unexpected behavior, denial of service, or even remote code execution in some specific scenarios. This issue has been patched in version 12.5.1. A workaround for this issue involves sanitizing the path argument provided to the set function to ensure that no part of the path string is __proto__, prototype, or constructor.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48054.json
- https://github.com/radashi-org/radashi/security/advisories/GHSA-2xv9-ghh9-xc69
- https://nvd.nist.gov/vuln/detail/CVE-2025-48054
- https://github.com/radashi-org/radashi/commit/8147abc8cfc3cfe9b9a17cd389076a5d97235a66
