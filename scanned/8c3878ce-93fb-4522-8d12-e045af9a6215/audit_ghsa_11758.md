# [C] Incus vulnerable to arbitrary file read and write through pongo templates

## Summary
Severity: Critical
Advisory: GHSA-83xr-5xxr-mh92
CVE: CVE-2026-33897
CWE: CWE-1336
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-83xr-5xxr-mh92
Type: github-advisory

## Affected
- Go: `github.com/lxc/incus/v6` — affected >=0 <6.23.0
- Go: `github.com/lxc/incus` — affected >=0

## Details
### Summary
Instance template files can be used to cause arbitrary read or writes as root on the host server.

### Details
Incus allows for pongo2 templates within instances which can be used at various times in the instance lifecycle to template files inside of the instance. This particular implementation of pongo2 within Incus allowed for file read/write but with the expectation that the pongo2 chroot feature would isolate all such access to the instance's filesystem.

This was allowed such that a template could theoretically read a file and then generate a new version of said file.

Unfortunately the chroot isolation mechanism is entirely skipped by pongo2 leading to easy access to the entire system's filesystem with root privileges.

### Credit
This issue was discovered and reported by the team at [7asecurity](https://7asecurity.com/)

## References
- https://github.com/lxc/incus/security/advisories/GHSA-83xr-5xxr-mh92
- https://nvd.nist.gov/vuln/detail/CVE-2026-33897
- https://github.com/lxc/incus/commit/487edf5984fad89b0f762c03a7e211fdd38396fb
- https://github.com/lxc/incus
