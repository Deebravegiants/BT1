# [M] AshLua read operation aggregate bypasses the exposed-field allow-list, exposing private attributes

## Summary
Severity: Medium
Advisory: CVE-2026-82586
Aliases: EEF-CVE-2026-82586, GHSA-37jv-wc37-fhcw
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-07
Source: https://osv.dev/vulnerability/CVE-2026-82586
Type: osv

## Details
Improper Protection of Alternate Path vulnerability in ash-project ash_lua allows a user-supplied Lua script to read attributes that are not on the exposed-field allow-list.

AshLua exposes Ash resources to Lua scripts, gated by a manifest declaring which fields are exposed. The read action's operation aggregate path in AshLua.Runtime took the field name straight from the Lua call and resolved it with only String.to_existing_atom and Ash.Query.Aggregate.new!, neither of which consults the exposed-field allow-list the normal fields path enforces. A script can therefore read the value of any attribute of any record the actor may read, including private sensitive?: true columns, via resource.read({ operation = {"list", "hashed_password"} }); min and max give a value oracle. Anyone able to submit or influence a Lua script can reach this.

This issue affects ash_lua: from 0.1.0 before 0.2.1.

## References
- https://cna.erlef.org/cves/CVE-2026-82586.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-82586
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82586.json
- https://github.com/ash-project/ash_lua/security/advisories/GHSA-37jv-wc37-fhcw
- https://nvd.nist.gov/vuln/detail/CVE-2026-82586
- https://github.com/ash-project/ash_lua/commit/c0dfcd9494766d548178c37df0bd01cff378e1c7
- https://github.com/ash-project/ash_lua
