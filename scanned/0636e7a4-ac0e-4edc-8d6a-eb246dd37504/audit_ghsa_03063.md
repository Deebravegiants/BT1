# [M] pomerium_signature is not verified in middleware in github.com/pomerium/pomerium

## Summary
Severity: Medium
Advisory: GHSA-fv82-r8qv-ch4v
CVE: CVE-2021-29652
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-21
Source: https://github.com/advisories/GHSA-fv82-r8qv-ch4v
Type: github-advisory

## Affected
- Go: `github.com/pomerium/pomerium` — affected >=0.10.0 <0.13.4

## Details
### Impact
Some API endpoints under /.pomerium/ do not verify parameters with pomerium_signature. This could allow modifying parameters intended to be trusted to Pomerium. 

The issue mainly affects routes responsible for sign in/out, but does not introduce an authentication bypass.

### Specific Go Packages Affected
github.com/pomerium/pomerium/authenticate

### Patches
Patched in v0.13.4

### For more information
If you have any questions or comments about this advisory
* Open an issue in [pomerium](http://github.com/pomerium/pomerium)
* Email us at [security@pomerium.com](mailto:security@pomerium.com)

## References
- https://github.com/pomerium/pomerium/security/advisories/GHSA-fv82-r8qv-ch4v
- https://nvd.nist.gov/vuln/detail/CVE-2021-29652
- https://github.com/pomerium/pomerium/pull/2048
