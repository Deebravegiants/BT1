# [M] Ruby JSON: JSON::ResumableParser#partial_value dereferences a freed input buffer and crashes on truncated duplicate-key streams

## Summary
Severity: Medium
Advisory: CVE-2026-71847
Aliases: GHSA-9hj4-r449-hfvc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-71847
Type: osv

## Details
Ruby JSON is a JSON implementation for Ruby. From 2.20.0 until 2.21.2, Ruby's JSON native C extension clears the consumed JSON::ResumableParser input buffer but leaves state.start, state.cursor, and state.end pointing into released storage. When partial_value reconstructs an incomplete object containing duplicate keys, the duplicate-key warning path calls cursor_position, which dereferences those stale pointers. This results in a heap-use-after-free and can terminate the Ruby process. An attacker who can supply JSON stream data to an application using JSON::ResumableParser may cause process termination when the application calls partial_value on incomplete attacker-controlled input containing duplicate object keys. This issue has been fixed in version 2.21.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71847.json
- https://github.com/ruby/json/security/advisories/GHSA-9hj4-r449-hfvc
- https://nvd.nist.gov/vuln/detail/CVE-2026-71847
