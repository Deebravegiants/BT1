# [M] Buffa Vulnerable to Memory Exhaustion Denial of Service in decode_unknown_field via Unbounded Allocation

## Summary
Severity: Medium
Advisory: GHSA-f9qc-qg88-7pq5
CVE: CVE-2026-55407
CWE: CWE-400, CWE-770, CWE-789
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-f9qc-qg88-7pq5
Type: github-advisory

## Affected
- crates.io: `buffa` — affected >=0 <0.8.0

## Details
The `decode_unknown_field` function in buffa's protobuf decoder allocated heap memory in proportion to untrusted input (unknown fields in the serialized protobuf) without enforcing an allocation budget. Any message decoded from untrusted input using code generated with `preserve_unknown_fields=true` (the default) was affected. A small, well-formed payload of nested unknown fields inside a StartGroup could trigger roughly 22× memory amplification (e.g., a 64 MiB input forcing ~1.4 GB of heap allocation), and length-delimited unknown fields could be sized arbitrarily, enabling an unauthenticated attacker to crash a process via memory exhaustion. This was reachable from the default decode APIs, since the top-level message size cap did not account for in-decode amplification. 

For users of connectrpc - the DEFAULT_MAX_MESSAGE_SIZE for connectrpc is 4MiB, which limits amplification in the worst case to ~88 MiB of memory. A flood of concurrent requests with this pattern could still be used to exhaust available memory, however.

Users are advised to either set `preserve_unknown_fields=false` on their current generated code, or upgrade to 0.8.0, which enforces per-message unknown field count limits - this is configurable, with a default of 1 million unknown fields, or ~40MiB of allocation overhead per message.
Users are advised to update to the latest version, which enforces per-message unknown field count limits.

Thank you to @p80n-sec for reporting this issue.

## References
- https://github.com/anthropics/buffa/security/advisories/GHSA-f9qc-qg88-7pq5
- https://nvd.nist.gov/vuln/detail/CVE-2026-55407
- https://github.com/anthropics/buffa/pull/184
- https://github.com/anthropics/buffa/commit/278fa43fcff661d4ee6bd83b75955a153d4281fc
- https://github.com/anthropics/buffa
- https://github.com/anthropics/buffa/releases/tag/v0.8.0
