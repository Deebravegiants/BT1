# [C] Pterodactyl Wings vulnerable to improper isolation of server file access

## Summary
Severity: Critical
Advisory: GHSA-494h-9924-xww9
CVE: CVE-2024-27102
CWE: CWE-22, CWE-362, CWE-363
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-15
Source: https://github.com/advisories/GHSA-494h-9924-xww9
Type: github-advisory

## Affected
- Go: `github.com/pterodactyl/wings` — affected >=0 <1.11.9

## Details
### Impact

This vulnerability impacts anyone running the affected versions of Wings.  The vulnerability can potentially be used to access files and directories on the host system.  The full scope of impact is exactly unknown, but reading files outside of a server's base directory (sandbox root) is possible.

In order to use this exploit, an attacker must have an existing "server" allocated and controlled by Wings.  Details on the exploitation of this vulnerability are embargoed until March 27th, 2024 at 18:00 UTC.

### Resolution

In order to mitigate this vulnerability, a full rewrite of the entire server filesystem was necessary.  Because of this, the size of the patch is massive, however effort was made to reduce the amount of breaking changes.  While tests were written to ensure security and functionality, there may be some semantic differences of certain operations, such as different errors being returned for example.  If you notice any major semantic differences, please open an issue on our issue tracker so it can be resolved. <https://github.com/pterodactyl/panel/issues/new/choose>

### Patches

This vulnerability has been resolved in version `v1.11.9` of Wings.

Everyone should update to Wings `v1.11.9` (or newer).

### Workarounds

None.

## References
- https://github.com/pterodactyl/wings/security/advisories/GHSA-494h-9924-xww9
- https://nvd.nist.gov/vuln/detail/CVE-2024-27102
- https://github.com/pterodactyl/wings/commit/d1c0ca526007113a0f74f56eba99511b4e989287
- https://github.com/pterodactyl/wings
