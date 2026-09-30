# [C] Filter expression injection via forged keyset pagination cursor in Ash

## Summary
Severity: Critical
Advisory: CVE-2026-67579
Aliases: EEF-CVE-2026-67579, GHSA-3gq3-9xm3-c8v3
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-67579
Type: osv

## Details
Deserialization of Untrusted Data vulnerability in ash-project ash allows an unauthenticated attacker to inject a filter expression through a forged keyset pagination cursor, resulting in SQL injection or code execution depending on the data layer.

Read actions with keyset pagination decode the client-supplied page[:after] or page[:before] cursor in decode_values/2 in lib/ash/page/keyset.ex using non_executable_binary_to_term/2 with [:safe]. That guard blocks new atoms, funs, and ports, but not a struct built from atoms already interned in a running Ash application, so a decoded %Ash.Query.Call{} expression survives and is spliced into the keyset filter as a comparison value in do_filters/4 and evaluated. Because the cursor bypasses the Ash.Expr macro, the runtime never applies the private?/public? gate that would otherwise reject it. On AshPostgres the injected fragment is inlined into the SQL query; on the ETS and Simple data layers it is evaluated in-process as an arbitrary function call.

This issue affects ash: from 1.17.0 before 3.31.3.

## References
- https://cna.erlef.org/cves/CVE-2026-67579.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-67579
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67579.json
- https://github.com/ash-project/ash/security/advisories/GHSA-3gq3-9xm3-c8v3
- https://nvd.nist.gov/vuln/detail/CVE-2026-67579
- https://github.com/ash-project/ash/commit/91874dd5435bc0ffebd8a254acfa573b39b74520
- https://github.com/ash-project/ash
