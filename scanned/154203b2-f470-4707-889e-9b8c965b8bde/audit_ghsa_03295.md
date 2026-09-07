# [M] Denial-of-Service within Docker container

## Summary
Severity: Medium
Advisory: GHSA-jhj6-5mh6-4pvf
CVE: CVE-2020-26213
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-24
Source: https://github.com/advisories/GHSA-jhj6-5mh6-4pvf
Type: github-advisory

## Affected
- Go: `ktbs.dev/teler` — affected >=0 <0.0.1

## Details
### Impact
If you run teler inside a Docker container and encounter `errors.Exit` function, it will cause denial-of-service (`SIGSEGV`) because it doesn't get process ID and process group ID of teler properly to kills.

### Specific Go Packages Affected
ktbs.dev/teler/pkg/errors

### Patches
Upgrade to the >= 0.0.1 version.

### Workarounds
N/A

### References
- https://github.com/kitabisa/teler/commit/ec6082049dba9e44a21f35fb7b123d42ce1a1a7e

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Issues Section](https://github.com/kitabisa/teler/issues)
* Email us at [infosec@kitabisa.com](mailto:infosec@kitabisa.com)

## References
- https://github.com/kitabisa/teler/security/advisories/GHSA-jhj6-5mh6-4pvf
- https://nvd.nist.gov/vuln/detail/CVE-2020-26213
- https://github.com/kitabisa/teler/commit/ec6082049dba9e44a21f35fb7b123d42ce1a1a7e
- https://github.com/kitabisa/teler
