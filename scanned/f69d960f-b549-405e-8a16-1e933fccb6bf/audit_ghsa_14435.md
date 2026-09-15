# [M] runc AppArmor bypass with symlinked /proc

## Summary
Severity: Medium
Advisory: GHSA-g2j6-57v7-gm8c
CVE: CVE-2023-28642
CWE: CWE-281, CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2023-03-30
Source: https://github.com/advisories/GHSA-g2j6-57v7-gm8c
Type: github-advisory

## Affected
- Go: `github.com/opencontainers/runc` — affected >=0 <1.1.5

## Details
### Impact
It was found that AppArmor, and potentially SELinux, can be bypassed when `/proc` inside the container is symlinked with a specific mount configuration.

### Patches
Fixed in runc v1.1.5, by prohibiting symlinked `/proc`: https://github.com/opencontainers/runc/pull/3785

This PR fixes CVE-2023-27561 as well.

### Workarounds
Avoid using an untrusted container image.

## References
- https://github.com/opencontainers/runc/security/advisories/GHSA-g2j6-57v7-gm8c
- https://nvd.nist.gov/vuln/detail/CVE-2023-28642
- https://github.com/opencontainers/runc/pull/3785
- https://github.com/opencontainers/runc
- https://security.netapp.com/advisory/ntap-20241206-0005
