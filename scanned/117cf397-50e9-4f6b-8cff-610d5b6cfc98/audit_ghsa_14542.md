# [M] Juju controller - Arbitrary file reading vulnerability

## Summary
Severity: Medium
Advisory: GHSA-x5rv-w9pm-8qp8
CVE: CVE-2023-0092
CWE: CWE-22, CWE-73
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-01
Source: https://github.com/advisories/GHSA-x5rv-w9pm-8qp8
Type: github-advisory

## Affected
- Go: `github.com/juju/juju` — affected >=2.9.22 <2.9.38
- Go: `github.com/juju/juju` — affected >=3.0.0 <3.0.3

## Details
### Impact
An authenticated user who has read access to the juju controller model, may construct a remote request to download an arbitrary file from the controller's filesystem.

### Patches
Patched in juju 2.9.38 and juju 3.0.3
[juju/juju#ef803e2](https://github.com/juju/juju/commit/ef803e2a13692d355b784b7da8b4b1f01dab1556)

### Workarounds
Limit read access to the controller model to only trusted users.

## References
- https://github.com/juju/juju/security/advisories/GHSA-x5rv-w9pm-8qp8
- https://nvd.nist.gov/vuln/detail/CVE-2023-0092
- https://github.com/juju/juju/commit/ef803e2a13692d355b784b7da8b4b1f01dab1556
- https://bugs.launchpad.net/juju/+bug/1999622
- https://github.com/advisories/GHSA-x5rv-w9pm-8qp8
- https://github.com/juju/juju
