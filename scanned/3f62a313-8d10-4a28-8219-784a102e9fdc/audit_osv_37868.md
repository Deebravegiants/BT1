# [H] ClearanceKit: opfilter policy bypass via exchangedata and clone operations

## Summary
Severity: High
Advisory: CVE-2026-33632
Aliases: GHSA-wpxj-vhfp-hhvm
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:L/SI:N/SA:N)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-33632
Type: osv

## Details
ClearanceKit intercepts file-system access events on macOS and enforces per-process access policies. Prior to version 4.2.4, two file operation event types — ES_EVENT_TYPE_AUTH_EXCHANGEDATA and ES_EVENT_TYPE_AUTH_CLONE — were not intercepted by ClearanceKit's opfilter system extension, allowing local processes to bypass file access policies. Commit 6181c4a patches the vulnerability by subscribing to both event types and routing them through the existing policy evaluator. Users must upgrade to v4.2.4 or later and reactivate the system extension.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33632.json
- https://github.com/craigjbass/clearancekit/security/advisories/GHSA-wpxj-vhfp-hhvm
- https://nvd.nist.gov/vuln/detail/CVE-2026-33632
- https://github.com/craigjbass/clearancekit/commit/6181c4a22eccbeca973c77f4bd023eb795c13786
