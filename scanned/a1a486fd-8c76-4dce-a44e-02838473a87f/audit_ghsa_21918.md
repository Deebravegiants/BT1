# [H] Zip slip directory exploit in github.com/deislabs/oras

## Summary
Severity: High
Advisory: GHSA-g5v4-5x39-vwhx
CVE: CVE-2021-21272
CWE: CWE-22, CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-g5v4-5x39-vwhx
Type: github-advisory

## Affected
- Go: `github.com/deislabs/oras` — affected >=0 <0.9.0

## Details
### Impact
The directory support (#55) allows the downloaded gzipped tarballs to be automatically extracted to the user-specified directory where the tarball can have symbolic links and hard links.

A well-crafted tarball or tarballs allow malicious artifact providers linking, writing, or overwriting specific files on the host filesystem outside of the user-specified directory unexpectedly with the same permissions as the user who runs `oras pull`. 

Precisely, the following users of the affected versions are impacted
- `oras` CLI users who runs `oras pull`.
- Go programs, which invokes `github.com/deislabs/oras/pkg/content.FileStore`.

### Patches
The problem has been patched by the PR linked with this advisory. Users should upgrade their `oras` CLI and packages to `0.9.0`.

### Workarounds
For `oras` CLI users, there is no workarounds other than pulling from a trusted artifact provider.

For `oras` package users, the workaround is to not use `github.com/deislabs/oras/pkg/content.FileStore`, and use other content stores instead, or pull from a trusted artifact provider.

### References
- [Zip Slip](https://github.com/snyk/zip-slip-vulnerability)

### For more information
If you have any questions or comments about this advisory:
* Open an issue on the [GitHub repo](https://github.com/deislabs/oras)
* Email the [list of maintainers](https://github.com/deislabs/oras/blob/main/MAINTAINERS)

## References
- https://github.com/deislabs/oras/security/advisories/GHSA-g5v4-5x39-vwhx
- https://nvd.nist.gov/vuln/detail/CVE-2021-21272
- https://github.com/deislabs/oras/commit/96cd90423303f1bb42bd043cb4c36085e6e91e8e
- https://github.com/deislabs/oras
- https://github.com/deislabs/oras/releases/tag/v0.9.0
- https://pkg.go.dev/github.com/deislabs/oras/pkg/oras
- https://pkg.go.dev/vuln/GO-2021-0099
