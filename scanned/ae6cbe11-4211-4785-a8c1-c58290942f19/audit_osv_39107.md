# [H] Vaultwarden: Unconfirmed Owner Can Purge Entire Organization Vault

## Summary
Severity: High
Advisory: CVE-2026-43913
Aliases: GHSA-937x-3j8m-7w7p
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-43913
Type: osv

## Details
Vaultwarden is a Bitwarden-compatible server written in Rust. Prior to 1.35.5, Vaultwarden allows an unconfirmed organization owner to purge the entire organization vault. The organization invite flow uses a two-step process: accepting an invite transitions membership from Invited to Accepted, and a separate confirmation by an existing owner upgrades it to Confirmed. The POST /api/ciphers/purge endpoint uses plain Headers and only checks that the membership type is Owner without verifying that the membership status is Confirmed. An authenticated user who has been invited as an organization owner and has accepted the invite and has not yet been confirmed can call this endpoint to hard-delete all ciphers and attachments in the organization,
causing immediate organization-wide data loss. This vulnerability is fixed in 1.35.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43913.json
- https://github.com/dani-garcia/vaultwarden/security/advisories/GHSA-937x-3j8m-7w7p
- https://nvd.nist.gov/vuln/detail/CVE-2026-43913
