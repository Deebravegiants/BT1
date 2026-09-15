# [M] Vaultwarden: Server-side request forgery (SSRF) via Icon Endpoint Decimal/Hex/Octal IP Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-47160
Aliases: GHSA-72vh-x5jq-m82g
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-47160
Type: osv

## Details
Vaultwarden is a Bitwarden-compatible server written in Rust. Prior to 1.36.0, Vaultwarden's /icons/{domain}/icon.png endpoint used src/http_client.rs checks including should_block_address() and post_resolve() that missed decimal, hexadecimal, and octal IP representations, allowing SSRF through the icon-fetching HTTP client for blind internal network or port discovery. This issue is fixed in version 1.36.0.

## References
- https://github.com/dani-garcia/vaultwarden/releases/tag/1.36.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47160.json
- https://github.com/dani-garcia/vaultwarden/security/advisories/GHSA-72vh-x5jq-m82g
- https://nvd.nist.gov/vuln/detail/CVE-2026-47160
- https://github.com/dani-garcia/vaultwarden/commit/a354e57659d26149fde0d91b76f83fce94e8f277
- https://github.com/dani-garcia/vaultwarden/pull/7162
