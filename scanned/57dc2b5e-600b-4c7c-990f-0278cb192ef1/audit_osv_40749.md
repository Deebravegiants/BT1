# [M] Plug: quadratic-time decoding of nested query/body parameters enables denial of service

## Summary
Severity: Medium
Advisory: CVE-2026-54892
Aliases: EEF-CVE-2026-54892, GHSA-j43x-5hjq-rgxf
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-54892
Type: osv

## Details
Inefficient algorithmic complexity in Plug's nested-parameter decoder allows an unauthenticated remote attacker to cause denial of service. Plug.Conn.Query.decode/4 (and Plug.Conn.Query.decode_each/2) parse query strings and application/x-www-form-urlencoded request bodies. When a key contains many bracketed segments such as a[a][a][a]=1, the decoder walks the brackets and, for each of the N levels, performs a map operation keyed on an ever-growing binary prefix of the key, hashing the full byte range at each step. The total decode cost is therefore quadratic in the number of nesting levels.

With the default Plug.Parsers.URLENCODED body limit of 1,000,000 bytes, a single request can carry roughly 333,000 nesting levels and saturate a BEAM scheduler for minutes. A small number of concurrent requests can saturate all schedulers and render a Plug-based server unresponsive. No authentication or knowledge of application routes is required.

This vulnerability is associated with program files lib/plug/conn/query.ex and program routines Plug.Conn.Query.decode/4, Plug.Conn.Query.decode_each/2, Plug.Conn.Query.split_keys/6, Plug.Conn.Query.insert_keys/3, and Plug.Conn.Query.finalize_pointer/2.

This issue affects plug from 1.15.0 before 1.15.5, 1.16.4, 1.17.2, 1.18.3, and 1.19.3.

## References
- https://cna.erlef.org/cves/CVE-2026-54892.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-54892
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54892.json
- https://github.com/elixir-plug/plug/security/advisories/GHSA-j43x-5hjq-rgxf
- https://nvd.nist.gov/vuln/detail/CVE-2026-54892
- https://github.com/elixir-plug/plug/commit/9c5d37c440eaae92869eed7c014c47266744fadb
- https://github.com/elixir-plug/plug/commit/a61124aa625d819a218fb07f90afbac8aa85eb0e
- https://github.com/elixir-plug/plug/commit/c317d08fdcf96e17931f7419275b2b8c4bf3e951
- https://github.com/elixir-plug/plug/commit/d4e5568392a4b29e545b91e12e87d6098f976145
- https://github.com/elixir-plug/plug/commit/d737eb236f17e31a36290e39f9ef3cd86a1343bd
- https://github.com/elixir-plug/plug
