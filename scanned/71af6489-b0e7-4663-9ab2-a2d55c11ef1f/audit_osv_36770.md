# [H] Potential information leakage from manager /network/graph API in NeuVector

## Summary
Severity: High
Advisory: CVE-2026-25703
Aliases: GHSA-hx45-873x-74qv
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-25703
Type: osv

## Details
NeuVector through 5.4.9 is can potentially leak information from manager /network/graph API due to missing authentication and cached data containing sensitive information.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25703.json
- https://github.com/neuvector/manager/security/advisories/GHSA-hx45-873x-74qv
- https://nvd.nist.gov/vuln/detail/CVE-2026-25703
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2026-25703
- https://github.com/neuvector/manager
