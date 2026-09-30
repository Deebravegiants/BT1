# [H] AntSword: Incomplete noxss() sanitization leads to 1-click RCE via jquery.terminal format code injection

## Summary
Severity: High
Advisory: CVE-2026-43892
Aliases: GHSA-c63g-p4cp-r45x
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-43892
Type: osv

## Details
AntSword is a cross-platform website management toolkit. Prior to 2.1.16, incomplete noxss() sanitization leads to 1-click RCE via jquery.terminal format code injection. This vulnerability is fixed in 2.1.16.

## References
- https://github.com/AntSwordProject/antSword/security/advisories/GHSA-c63g-p4cp-r45x
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43892.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43892
