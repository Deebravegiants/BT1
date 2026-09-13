# [C] CVE-2026-38968

## Summary
Severity: Critical
Advisory: CVE-2026-38968
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-38968
Type: osv

## Details
ntopng through 6.6 is vulnerable to Predictable Session Identifier which can lead to Session Hijacking. HTTP session identifiers in src/HTTPserver.cpp use weak time-seeded pseudo-randomness during session creation. As a result, fresh authenticated logins can receive deterministic or colliding session cookies under attacker-controlled timing.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/38xxx/CVE-2026-38968.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-38968
- https://github.com/ntop/ntopng/commit/14e22497233dc7d31d19dccb74b13bb073d16c2c
- https://github.com/ntop/ntopng/commit/179a346ceb6239fd36128ccca3efa8f9ea61eeb5
