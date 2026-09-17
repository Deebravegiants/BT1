# [M] SQL injection via the :comment option in Postgrex.stream/4

## Summary
Severity: Medium
Advisory: CVE-2026-66838
Aliases: EEF-CVE-2026-66838, GHSA-3gww-3f36-2388
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-66838
Type: osv

## Details
Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection') vulnerability in elixir-ecto postgrex allows SQL Injection via the :comment option of Postgrex.stream/4. An attacker who can influence that value can close the comment delimiter with */ and extend the streamed statement with their own clauses, which execute under the connection's role. Ecto exposes the same option through Ecto.Repo.stream/2.

Postgrex appends the comment by concatenating it into the statement text sent in the Parse message, without escaping or rejecting */. The option is validated by comment_not_present!/1 at every other execution point; stream/4 never calls it. Because Parse accepts a single command, the injection is confined to the streamed statement and further statements cannot be chained.

This issue affects postgrex: from 0.19.3 before 0.22.4.

## References
- https://cna.erlef.org/cves/CVE-2026-66838.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-66838
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66838.json
- https://github.com/elixir-ecto/ecto/security/advisories/GHSA-3gww-3f36-2388
- https://nvd.nist.gov/vuln/detail/CVE-2026-66838
- https://github.com/elixir-ecto/postgrex/commit/4011be852c99dc61ddb98cb01aa41e8775a0e3dd
- https://github.com/elixir-ecto/postgrex/commit/e1ecba618ddea4cee2556bd6ad9b6285e05f9d3c
- https://github.com/elixir-ecto/postgrex
