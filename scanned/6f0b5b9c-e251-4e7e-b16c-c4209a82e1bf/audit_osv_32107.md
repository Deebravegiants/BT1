# [H] vaultwarden allows escalation of privilege via variable confusion in OrgHeaders trait

## Summary
Severity: High
Advisory: CVE-2025-24365
Aliases: GHSA-j4h8-vch3-f797
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-01-27
Source: https://osv.dev/vulnerability/CVE-2025-24365
Type: osv

## Details
vaultwarden is an unofficial Bitwarden compatible server written in Rust, formerly known as bitwarden_rs. Attacker can obtain owner rights of other organization. Hacker should know the ID of victim organization (in real case the user can be a part of the organization as an unprivileged user) and be the owner/admin of other organization (by default you can create your own organization) in order to attack. This vulnerability is fixed in 1.33.0.

## References
- https://github.com/dani-garcia/vaultwarden/releases/tag/1.33.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24365.json
- https://github.com/dani-garcia/vaultwarden/security/advisories/GHSA-j4h8-vch3-f797
- https://nvd.nist.gov/vuln/detail/CVE-2025-24365
