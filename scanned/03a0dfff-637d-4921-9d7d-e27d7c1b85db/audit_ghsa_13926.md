# [C] Pterodactyl Wings contains UNIX Symbolic Link (Symlink) Following resulting in deletion of files and directories on the host system

## Summary
Severity: Critical
Advisory: GHSA-66p8-j459-rq63
CVE: CVE-2023-25168
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2023-02-10
Source: https://github.com/advisories/GHSA-66p8-j459-rq63
Type: github-advisory

## Affected
- Go: `github.com/pterodactyl/wings` — affected >=0 <1.7.4
- Go: `github.com/pterodactyl/wings` — affected >=1.11.0 <1.11.4

## Details
### Impact

This vulnerability impacts anyone running the affected versions of Wings.  The vulnerability can be used to delete files and directories recursively on the host system.  This vulnerability can be combined with [`GHSA-p8r3-83r8-jwj5`](https://github.com/pterodactyl/wings/security/advisories/GHSA-p8r3-83r8-jwj5) to overwrite files on the host system.

In order to use this exploit, an attacker must have an existing "server" allocated and controlled by Wings.  Information on how the exploitation of this vulnerability works will be released on February 24th, 2023 in North America.

### Patches

This vulnerability has been resolved in version `v1.11.4` of Wings, and has been back-ported to the 1.7 release series in `v1.7.4`.

Anyone running `v1.11.x` should upgrade to `v1.11.4` and anyone running `v1.7.x` should upgrade to `v1.7.4`.

### Workarounds

None at this time.

## References
- https://github.com/pterodactyl/wings/security/advisories/GHSA-66p8-j459-rq63
- https://github.com/pterodactyl/wings/security/advisories/GHSA-p8r3-83r8-jwj5
- https://nvd.nist.gov/vuln/detail/CVE-2023-25168
- https://github.com/pterodactyl/wings/commit/429ac62dba22997a278bc709df5ac00a5a25d83d
- https://github.com/pterodactyl/wings
