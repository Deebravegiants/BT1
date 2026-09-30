# [M] Console is vulnerable to path traversal regarding custom assets

## Summary
Severity: Medium
Advisory: CVE-2025-65952
Aliases: GHSA-c3f7-xh45-2xc7
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/CVE-2025-65952
Type: osv

## Details
Console is a network used to control Gorilla Tag mods' users and other users on the network. Prior to version 2.8.0, a path traversal vulnerability exists where complicated combinations of backslashes and periods can be used to escape the Gorilla Tag path and write to unwanted directories. This issue has been patched in version 2.8.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65952.json
- https://github.com/iiDk-the-actual/Console/security/advisories/GHSA-c3f7-xh45-2xc7
- https://nvd.nist.gov/vuln/detail/CVE-2025-65952
- https://github.com/iiDk-the-actual/Console/commit/4bcb1cf23ef78f8e6899dd6fe3afa3b24902e458
- https://github.com/iiDk-the-actual/Console/commit/e1005b8754594ad463ae58f8a99decda548b1826
