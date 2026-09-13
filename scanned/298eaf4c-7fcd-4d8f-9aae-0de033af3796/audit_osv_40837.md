# [M] Atom-table exhaustion denial of service in Guardian permissions AtomEncoding via unbounded atom creation

## Summary
Severity: Medium
Advisory: CVE-2026-55733
Aliases: EEF-CVE-2026-55733, GHSA-fjr5-7xrc-hmpj
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-55733
Type: osv

## Details
Allocation of Resources Without Limits or Throttling in ueberauth guardian allows denial of service via unbounded atom creation from attacker-controlled binary input.

Guardian.Permissions.AtomEncoding encodes permission scopes by passing arbitrary binaries to String.to_atom/1. When encode/3 in lib/guardian/permissions/atom_encoding.ex is called with a list, each binary entry is handled by the encode_value/3 binary clause, which calls String.to_atom(value) with no allow-list check. The perm_set argument (the application's small, finite set of legitimate permission names) is discarded, so any external string flows straight into atom creation. This encoder is selected with use Guardian.Permissions, encoding: Guardian.Permissions.AtomEncoding and reached through the imported encode/3 entry point.

String.to_atom/1 creates a brand-new atom for every previously unseen binary, atoms are never garbage collected, and the BEAM atom table is fixed at roughly 1,048,576 entries by default. An application that funnels attacker-influenced permission scopes (from a request body, a JWT claim, or other external input) into encode/3 therefore mints one permanent atom per distinct value. A modest stream of varied, unauthenticated input permanently consumes the atom table and crashes the BEAM node with system_limit, taking down every application running on it.

The default encoder is Guardian.Permissions.BitwiseEncoding, which is not affected.

This issue affects guardian: from 2.0.0 before 2.4.1.

## References
- https://cna.erlef.org/cves/CVE-2026-55733.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-55733
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55733.json
- https://github.com/ueberauth/guardian/security/advisories/GHSA-fjr5-7xrc-hmpj
- https://nvd.nist.gov/vuln/detail/CVE-2026-55733
- https://github.com/ueberauth/guardian/commit/9cd268557846aa4c3ad53566c08f2c190ee5513f
- https://github.com/ueberauth/guardian
