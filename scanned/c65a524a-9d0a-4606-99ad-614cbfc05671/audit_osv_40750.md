# [M] Atom-table exhaustion denial of service in Guardian via unbounded atom creation from binary keys

## Summary
Severity: Medium
Advisory: CVE-2026-54894
Aliases: EEF-CVE-2026-54894, GHSA-xqch-c77q-rgh5
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-54894
Type: osv

## Details
Allocation of Resources Without Limits or Throttling in ueberauth guardian allows denial of service via unbounded atom creation from attacker-influenced binary input.

Guardian.Plug.Keys derives connection and session namespace keys by passing arbitrary binaries to String.to_atom/1. base_key/1 in lib/guardian/plug/keys.ex converts any binary into the atom :"guardian_<input>", and the derived helpers claims_key/1, resource_key/1, and token_key/1 create a second atom on top of that. key_from_other/1 likewise converts a regex-captured binary through String.to_atom/1. The public specs advertise String.t() as a valid argument, so passing a string is documented usage, and higher-level entry points such as Guardian.Plug.current_token(conn, key: key) thread the caller-supplied key straight into these functions.

String.to_atom/1 creates a brand-new atom for every previously unseen binary, atoms are never garbage collected, and the BEAM atom table is fixed at roughly 1,048,576 entries by default. An application that routes attacker-influenced data (a tenant identifier, header, or other request input) into a Guardian key therefore mints one permanent atom per distinct value. A modest stream of varied, unauthenticated input permanently consumes the atom table and crashes the BEAM node, taking down every application running on it.

This issue affects guardian: from 0.1.0 before 2.4.1.

## References
- https://cna.erlef.org/cves/CVE-2026-54894.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-54894
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54894.json
- https://github.com/ueberauth/guardian/security/advisories/GHSA-xqch-c77q-rgh5
- https://nvd.nist.gov/vuln/detail/CVE-2026-54894
- https://github.com/ueberauth/guardian/commit/2952657e42e6341a67e6aaad09d8f0b40ae917cb
- https://github.com/ueberauth/guardian
