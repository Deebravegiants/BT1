# [M] Atom Exhaustion via _entities Representation Keys in DivvyPayHQ absinthe_federation

## Summary
Severity: Medium
Advisory: CVE-2026-67585
Aliases: EEF-CVE-2026-67585, GHSA-55hv-mwvr-phf3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-67585
Type: osv

## Details
Allocation of Resources Without Limits or Throttling vulnerability in DivvyPayHQ absinthe_federation allows an unauthenticated remote attacker to abort the Erlang VM via crafted _entities representation keys.

Every key of every object in the representations argument of the federation-mandated _entities field is converted with String.to_atom/1 by convert_key/2 in lib/absinthe/federation/schema/entities_field.ex. representations is typed as the open-ended _Any scalar, so its keys bypass schema coercion and the attacker names them freely. Atoms are never garbage collected and the BEAM atom table is hard-capped (about 1,048,576 entries by default), so one request carrying tens of thousands of unique keys creates that many permanent atoms and a handful of such requests exhausts the table and aborts the node. The impact is confined to availability: no data is read or altered, and recovery requires restarting the application.

This issue affects absinthe_federation: from 0.1.0 before 0.9.3.

## References
- https://cna.erlef.org/cves/CVE-2026-67585.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-67585
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67585.json
- https://github.com/DivvyPayHQ/absinthe_federation/security/advisories/GHSA-55hv-mwvr-phf3
- https://nvd.nist.gov/vuln/detail/CVE-2026-67585
- https://github.com/DivvyPayHQ/absinthe_federation/commit/c3838cda2a7f65c4893291668c223b0d6acf4516
- https://github.com/DivvyPayHQ/absinthe_federation
