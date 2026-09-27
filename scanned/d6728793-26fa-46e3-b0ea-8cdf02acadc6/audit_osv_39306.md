# [H] MapServer: NULL pointer dereference in SLD `<ElseFilter>` rule parsing reachable via WMS `SLD_BODY`

## Summary
Severity: High
Advisory: CVE-2026-45104
Aliases: GHSA-4h8g-378q-r75m
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45104
Type: osv

## Details
MapServer is a system for developing web-based GIS applications. From 6.4.0 to before 8.6.3, msSLDParseUserStyle always calls _SLDApplyRuleValues(psRule, psLayer, 1); for any <Rule> carrying <ElseFilter/> — it assumes msSLDParseRule added one class. When the rule has no symbolizer (a structurally valid SLD), msSLDParseRule adds zero, and _SLDApplyRuleValues ends up indexing _class[-1], resulting in a NULL pointer dereference. A 200-byte well-formed SLD via the WMS SLD_BODY= parameter is enough to trigger this, no auth required. This vulnerability is fixed in 8.6.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45104.json
- https://github.com/MapServer/MapServer/security/advisories/GHSA-4h8g-378q-r75m
- https://nvd.nist.gov/vuln/detail/CVE-2026-45104
