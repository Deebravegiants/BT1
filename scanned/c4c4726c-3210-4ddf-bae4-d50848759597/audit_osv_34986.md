# [M] CVE-2025-67125

## Summary
Severity: Medium
Advisory: CVE-2025-67125
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2025-67125
Type: osv

## Details
A signed integer overflow in docopt.cpp v0.6.2 (LeafPattern::match in docopt_private.h) when merging occurrence counters (e.g., default LONG_MAX + first user "-v/--verbose") can cause counter wrap (negative/unbounded semantics) and lead to logic/policy bypass in applications that rely on occurrence-based limits, rate-gating, or safety toggles. In hardened builds (e.g., UBSan or -ftrapv), the overflow may also result in process abort (DoS).

## References
- https://gist.github.com/thesmartshadow/672afe8828844c833f46f8ebe2f5f3bd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67125.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-67125
- https://github.com/docopt/docopt.cpp
