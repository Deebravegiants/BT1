# [M] Private action arguments can be set by user input in Ash

## Summary
Severity: Medium
Advisory: CVE-2026-55736
Aliases: EEF-CVE-2026-55736, GHSA-f4hc-ppw9-4hhw
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-55736
Type: osv

## Details
Improperly Controlled Modification of Dynamically-Determined Object Attributes vulnerability in ash-project ash allows a user to set the value of a private action argument that is intended to be controlled only by trusted server-side code.

Action arguments declared with public?: false are meant to be set internally (for example via Ash.Changeset.set_private_argument/3) and must not be settable from end-user input. When a changeset is built from a parameter map, Ash filters out private arguments, but the filtering is incomplete.

In the regular changeset path (for_create, for_update, for_destroy), private arguments are stripped only when the parameter key is an atom. When the key is a binary (string), as is the case for user-supplied parameters, the private argument is kept and the user controls its value. In the atomic path (Ash.Changeset.fully_atomic_changeset/4, also reached through atomic and bulk updates), private arguments are not stripped at all, regardless of whether the key is an atom or a binary.

An attacker who can submit parameters to an action that defines a private argument can therefore inject a value for that argument. Depending on how the application uses the argument (for example an acting_user_id driving authorization or record ownership), this can lead to an integrity violation or privilege escalation.

This issue affects ash: from 3.0.0 before 3.29.3.

## References
- https://cna.erlef.org/cves/CVE-2026-55736.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-55736
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55736.json
- https://github.com/ash-project/ash/security/advisories/GHSA-f4hc-ppw9-4hhw
- https://nvd.nist.gov/vuln/detail/CVE-2026-55736
- https://github.com/ash-project/ash/commit/d9b3100219b3ea86d73202bf7368c03a7688efea
- https://github.com/ash-project/ash
