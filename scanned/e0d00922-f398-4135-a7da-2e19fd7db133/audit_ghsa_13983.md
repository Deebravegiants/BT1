# [H] mrpack-install vulnerable to path traversal with dependency

## Summary
Severity: High
Advisory: GHSA-r887-gfxh-m9rr
CVE: CVE-2023-25307
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-08
Source: https://github.com/advisories/GHSA-r887-gfxh-m9rr
Type: github-advisory

## Affected
- Go: `github.com/nothub/mrpack-install` — affected >=0 <0.16.3

## Details
### Impact
Importing a malicious `.mrpack` file can cause path traversal while downloading files.
This can lead to scripts or config files being placed or replaced at arbitrary locations, without the user noticing.

### Patches
No patches yet.

### Workarounds
Avoid importing `.mrpack` files from untrusted sources.

### References
https://docs.modrinth.com/docs/modpacks/format_definition/#files

## References
- https://github.com/nothub/mrpack-install/security/advisories/GHSA-r887-gfxh-m9rr
- https://nvd.nist.gov/vuln/detail/CVE-2023-25307
- https://github.com/nothub/mrpack-install/commit/a1f424b6a616d2de95228781eef3b92b9769f23c
- https://github.com/nothub/mrpack-install
- https://github.com/nothub/mrpack-install/releases/tag/v0.16.3
- https://quiltmc.org/en/blog/2023-02-04-five-installer-vulnerabilities
