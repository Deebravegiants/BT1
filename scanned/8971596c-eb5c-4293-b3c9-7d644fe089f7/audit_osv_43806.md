# [M] Unbounded atom creation from client-supplied RPC field names in AshTypescript field formatter

## Summary
Severity: Medium
Advisory: CVE-2026-74837
Aliases: EEF-CVE-2026-74837, GHSA-mhxc-mhqx-3v28
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-74837
Type: osv

## Details
Allocation of Resources Without Limits or Throttling vulnerability in ash-project ash_typescript allows an unauthenticated attacker to exhaust the BEAM atom table and abort the node via client-supplied RPC field names.

AshTypescript.FieldFormatter.convert_to_field_atom/2 in lib/ash_typescript/field_formatter.ex converts a client-supplied field name to an atom with String.to_atom/1 when no matching atom already exists. It delegates first to parse_input_field/2, which resolves the name with String.to_existing_atom/1 and falls back to returning the plain string; convert_to_field_atom/2 then mints an atom from that string rather than treating the name as unknown.

RPC field selection reaches it for every requested field name through AshTypescript.Rpc.FieldProcessing.FieldSelector, which resolves each name before checking that the field exists, with no allowlist, length bound, or rate limit. Atoms are never garbage collected, so each distinct name mints a permanent one and the VM aborts once the atom table limit is reached. A field name over 255 characters additionally raises an uncaught SystemLimitError.

This issue affects ash_typescript: from 0.1.0 before 0.18.0.

## References
- https://cna.erlef.org/cves/CVE-2026-74837.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-74837
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74837.json
- https://github.com/ash-project/ash_typescript/security/advisories/GHSA-mhxc-mhqx-3v28
- https://nvd.nist.gov/vuln/detail/CVE-2026-74837
- https://github.com/ash-project/ash_typescript/commit/df95df4b9afdca5e5bbce32dbd566ccc49a7f14b
- https://github.com/ash-project/ash_typescript
