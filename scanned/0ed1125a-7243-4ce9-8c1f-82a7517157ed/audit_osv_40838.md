# [M] guardian atom exhaustion in Guardian.Permissions.encode_permissions!/1

## Summary
Severity: Medium
Advisory: CVE-2026-55734
Aliases: EEF-CVE-2026-55734, GHSA-9qx2-v587-q3gg
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-55734
Type: osv

## Details
Allocation of Resources Without Limits or Throttling vulnerability in ueberauth guardian (Guardian.Permissions module) allows a denial of service via BEAM atom-table exhaustion.

This vulnerability is associated with program file lib/guardian/permissions.ex and program routines 'Elixir.Guardian.Permissions':encode_permissions!/1, 'Elixir.Guardian.Permissions':encode_permissions_into_claims!/2, 'Elixir.Guardian.Permissions':do_encode_permissions!/2.

The Guardian.Permissions mixin installs a public encode_permissions!/1 function on every module that does use Guardian.Permissions. For each key of the supplied map, encode_permissions!/1 calls String.to_atom(to_string(k)) before any validation runs. The integer-value clause of do_encode_permissions!/2 then short-circuits straight to encoding without validating the key against the configured permission set, so a key with an integer value is interned as a fresh atom with no exception raised. Atoms are never garbage collected and the BEAM atom table is a fixed-size resource (default roughly 1,048,576 entries), so each unique attacker-chosen key permanently consumes one slot. An attacker who can influence a permission map that reaches encode_permissions!/1 (for example a permissions map read from a request body and passed into token issuance via encode_permissions_into_claims!/2) can mint an unbounded number of atoms and exhaust the atom table, crashing the entire BEAM node and every service running on it. The sibling decode_permissions/1 is not affected because it skips keys absent from the configured permission set.

This issue affects guardian: from 2.0.0 before 2.4.1.

## References
- https://cna.erlef.org/cves/CVE-2026-55734.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-55734
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55734.json
- https://github.com/ueberauth/guardian/security/advisories/GHSA-9qx2-v587-q3gg
- https://nvd.nist.gov/vuln/detail/CVE-2026-55734
- https://github.com/ueberauth/guardian/commit/8d4efbfc352d30f5fcfc75a4d69a795b0e472724
- https://github.com/ueberauth/guardian
