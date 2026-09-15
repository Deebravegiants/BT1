# [C] Concrete CMS below 9.5.2 is vulnerable to PHP Object Injection via unserialize() calls in the  in Permission, Cache, and Search components

## Summary
Severity: Critical
Advisory: CVE-2026-10721
Aliases: GHSA-g82f-9pw7-773w
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-10721
Type: osv

## Details
Concrete CMS below 9.5.2 is vulnerable to PHP Object Injection via unserialize() calls in the  in Permission, Cache, and Search components. An unauthenticated attacker may trigger arbitrary PHP object instantiation if a malicious serialized payload has been placed in the database. Thanks XananasX7 for reporting.

## References
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/952-release-notes
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10721.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-10721
- https://github.com/concretecms/concretecms
