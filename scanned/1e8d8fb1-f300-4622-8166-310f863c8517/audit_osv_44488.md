# [M] Match regex runs on over-length input in Ash.Type.String, enabling regex denial of service

## Summary
Severity: Medium
Advisory: CVE-2026-82735
Aliases: EEF-CVE-2026-82735, GHSA-mq7g-pffw-m8xh
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-82735
Type: osv

## Details
Uncontrolled Resource Consumption vulnerability in ash-project ash allows an attacker to force an expensive regular expression to run on input that a length constraint should have already rejected.

Ash.Type.String.apply_constraints/2 (lib/ash/type/string.ex) evaluated the :match regex regardless of the min_length and max_length constraints on the same attribute. Because the length check did not gate the regex, an over-length value that the length constraint rejects still had the pattern applied to it, so the length limit that would otherwise bound the work never constrained the regex input. Against a backtracking pattern this yields catastrophic regex evaluation on attacker-sized input, and even a linear pattern runs on arbitrarily large input, consuming CPU per request. The fix skips the :match regex whenever a length constraint is violated, making the two checks order-independent.

This issue affects ash: from 0.10.0 before 3.32.2.

## References
- https://cna.erlef.org/cves/CVE-2026-82735.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-82735
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82735.json
- https://github.com/ash-project/ash/security/advisories/GHSA-mq7g-pffw-m8xh
- https://nvd.nist.gov/vuln/detail/CVE-2026-82735
- https://github.com/ash-project/ash/commit/14928412a1a94a69c47df8e98920d3a2b09cdec4
- https://github.com/ash-project/ash
