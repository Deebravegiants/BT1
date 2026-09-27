# [M] vaultwarden has Full Cipher Enumeration Ignoring Organization Collection Permissions

## Summary
Severity: Medium
Advisory: CVE-2026-26012
Aliases: GHSA-h265-g7rm-h337
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-11
Source: https://osv.dev/vulnerability/CVE-2026-26012
Type: osv

## Details
vaultwarden is an unofficial Bitwarden compatible server written in Rust, formerly known as bitwarden_rs. Prior to 1.35.3, a regular organization member can retrieve all ciphers within an organization, regardless of collection permissions. The endpoint /ciphers/organization-details is accessible to any organization member and internally uses Cipher::find_by_org to retrieve all ciphers. These ciphers are returned with CipherSyncType::Organization without enforcing collection-level access control. This vulnerability is fixed in 1.35.3.

## References
- https://github.com/dani-garcia/vaultwarden/releases/tag/1.35.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26012.json
- https://github.com/dani-garcia/vaultwarden/security/advisories/GHSA-h265-g7rm-h337
- https://nvd.nist.gov/vuln/detail/CVE-2026-26012
