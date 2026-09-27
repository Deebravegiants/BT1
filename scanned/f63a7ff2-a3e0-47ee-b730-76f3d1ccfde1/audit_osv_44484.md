# [M] AshAdmin LiveView events intern atoms from client input, exhausting the atom table (node DoS)

## Summary
Severity: Medium
Advisory: CVE-2026-82722
Aliases: EEF-CVE-2026-82722, GHSA-wcr6-9rrw-5jhv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-82722
Type: osv

## Details
Allocation of Resources Without Limits or Throttling vulnerability in ash-project ash_admin lets any client that can reach the admin LiveView exhaust the BEAM atom table and crash the entire node.

Two LiveView event handlers interned atoms from unvalidated client input: AshAdmin.PageLive's set_actor built modules from the resource/domain payload with Module.concat/1, and AshAdmin.Components.Resource.Show's calculate converted every submitted form key with String.to_atom/1. Atoms are never garbage collected and the table is capped, so flooding either event with random names mints a new atom per request until the VM aborts, taking down every application on the node. The fix resolves the submitted resource/domain against the known shown resources and maps calculation keys to declared arguments, so no client-supplied string is interned.

This issue affects ash_admin: from 0.1.0 before 1.3.1.

## References
- https://cna.erlef.org/cves/CVE-2026-82722.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-82722
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82722.json
- https://github.com/ash-project/ash_admin/security/advisories/GHSA-wcr6-9rrw-5jhv
- https://nvd.nist.gov/vuln/detail/CVE-2026-82722
- https://github.com/ash-project/ash_admin/commit/731dffa09416d68f4ad3a0b6ee146b285ca0083b
- https://github.com/ash-project/ash_admin
