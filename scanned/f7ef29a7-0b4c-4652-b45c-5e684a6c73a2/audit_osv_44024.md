# [M] Unbounded atom creation from typed struct field names in AshTypescript field selector

## Summary
Severity: Medium
Advisory: CVE-2026-77856
Aliases: EEF-CVE-2026-77856, GHSA-rj47-h936-4cxw
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-77856
Type: osv

## Details
Allocation of Resources Without Limits or Throttling vulnerability in ash-project ash_typescript allows an unauthenticated attacker to exhaust the BEAM atom table and abort the node via client-supplied typed struct field names.

resolve_typed_struct_field/2 in lib/ash_typescript/rpc/field_processing/field_selector.ex looks a client-supplied field name up in the typed struct's reverse map and, when it finds no match, falls back to String.to_atom/1. Because this runs before any field-existence check, an unresolvable name mints a permanent atom rather than being rejected as unknown. Atoms are never garbage collected, so a request carrying many distinct names on a typed struct field grows the atom table until the VM aborts at its limit.

This issue affects ash_typescript: from 0.11.0 before 0.18.0.

## References
- https://cna.erlef.org/cves/CVE-2026-77856.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-77856
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77856.json
- https://github.com/ash-project/ash_typescript/security/advisories/GHSA-rj47-h936-4cxw
- https://nvd.nist.gov/vuln/detail/CVE-2026-77856
- https://github.com/ash-project/ash_typescript/commit/0ab5c83a7df28d51a6de1fb9b859a142b2b12919
- https://github.com/ash-project/ash_typescript
