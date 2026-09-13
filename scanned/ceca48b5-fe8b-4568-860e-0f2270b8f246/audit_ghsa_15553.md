# [M] Exposure of debug and metrics endpoints in Pomerium

## Summary
Severity: Medium
Advisory: GHSA-q98f-2x4p-prjr
CVE: CVE-2022-24797
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2024-09-06
Source: https://github.com/advisories/GHSA-q98f-2x4p-prjr
Type: github-advisory

## Affected
- Go: `github.com/pomerium/pomerium` — affected >=0.16.0 <0.17.1

## Details
### Impact
In distributed service mode, Pomerium's Authenticate service exposes pprof debug and prometheus metrics handlers to untrusted traffic.  This can leak potentially sensitive environmental information or lead to limited denial of service conditions.

### Patches
v0.17.1

### Workarounds
Block access to `/debug` and `/metrics` paths on the authenticate service.  This can be done with any L7 proxy, including Pomerium's own proxy service.

### References
https://github.com/pomerium/pomerium/pull/3212

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Pomerium](https://github.com/pomerium/pomerium)
* Email us at [security@pomerium.com](mailto:security@pomerium.com)

## References
- https://github.com/pomerium/pomerium/security/advisories/GHSA-q98f-2x4p-prjr
- https://nvd.nist.gov/vuln/detail/CVE-2022-24797
- https://github.com/pomerium/pomerium/pull/3212
- https://github.com/pomerium/pomerium/commit/b435f73e2b54088da2aca5e8c3aa1808293d6903
- https://github.com/pomerium/pomerium
- https://pkg.go.dev/vuln/GO-2022-0413
