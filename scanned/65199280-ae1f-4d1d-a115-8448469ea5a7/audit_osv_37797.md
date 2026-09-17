# [H] OpenEMR: zhAclCheck Ignores Explicit ACL Denies

## Summary
Severity: High
Advisory: CVE-2026-33302
Aliases: GHSA-v68v-pwc4-8p2m
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-33302
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to 8.0.0.2, the module ACL function `AclMain::zhAclCheck()` only checks for the presence of any "allow" (user or group). It never checks for explicit "deny" (allowed=0). As a result, administrators cannot revoke access by setting a user or group to "deny"; if the user is in a group that has "allow," access is granted regardless of explicit denies. Version 8.0.0.2 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33302.json
- https://github.com/openemr/openemr/security/advisories/GHSA-v68v-pwc4-8p2m
- https://nvd.nist.gov/vuln/detail/CVE-2026-33302
- https://github.com/openemr/openemr/commit/0ef9b1763029e52d43fcb4fd0ebb0769a7ec43d4
