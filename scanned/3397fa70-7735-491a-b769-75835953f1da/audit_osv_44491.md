# [M] Ash.Filter.Runtime materializes a combinatorial cross-product over to-many relationships, exhausting memory

## Summary
Severity: Medium
Advisory: CVE-2026-82742
Aliases: EEF-CVE-2026-82742, GHSA-mgwj-c69v-6f83
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-82742
Type: osv

## Details
Uncontrolled Resource Consumption vulnerability in ash-project ash lets an attacker exhaust node memory by matching a filter that spans multiple to-many relationships in memory.

Ash.Filter.Runtime matches a filter against an in-memory record by first expanding the record into combinations of its related rows. flatten_relationships/2 (lib/ash/filter/runtime.ex) eagerly built the full Cartesian product across the filter's to-many relationship paths, so a record with K to-many relationships of M rows each materialized on the order of M^K scenarios before any predicate was checked. A filter or dataset that reaches several sizeable to-many relationships therefore allocates memory combinatorially and can exhaust the node. The fix streams the expansion lazily and short-circuits on the first matching scenario, bounding the work.

This issue affects ash: from 1.29.0-rc0 before 3.32.2.

## References
- https://cna.erlef.org/cves/CVE-2026-82742.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-82742
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82742.json
- https://github.com/ash-project/ash/security/advisories/GHSA-mgwj-c69v-6f83
- https://nvd.nist.gov/vuln/detail/CVE-2026-82742
- https://github.com/ash-project/ash/commit/da07f009e889819ec410fa1f0f12534bfb9e21dd
- https://github.com/ash-project/ash
