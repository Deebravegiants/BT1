# [H] Pterodactyl Wings vulnerable to Arbitrary File Write/Read

## Summary
Severity: High
Advisory: GHSA-gqmf-jqgv-v8fw
CVE: CVE-2024-34066
CWE: CWE-552
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-03
Source: https://github.com/advisories/GHSA-gqmf-jqgv-v8fw
Type: github-advisory

## Affected
- Go: `github.com/pterodactyl/wings` — affected >=0 <1.11.12

## Details
### Impact

If the Wings token is leaked either by viewing the node configuration or posting it accidentally somewhere, an attacker can use it to gain arbitrary file write and read access on the node the token is associated to.

### Workarounds

Enabling the `ignore_panel_config_updates` option or updating to the latest version of Wings are the only known workarounds.

### Patches

https://github.com/pterodactyl/wings/commit/5415f8ae07f533623bd8169836dd7e0b933964de

## References
- https://github.com/pterodactyl/wings/security/advisories/GHSA-gqmf-jqgv-v8fw
- https://nvd.nist.gov/vuln/detail/CVE-2024-34066
- https://github.com/pterodactyl/wings/commit/5415f8ae07f533623bd8169836dd7e0b933964de
- https://github.com/pterodactyl/wings
