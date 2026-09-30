# [C] Vitess users with backup storage access can write to arbitrary file paths on restore

## Summary
Severity: Critical
Advisory: GHSA-r492-hjgh-c9gw
CVE: CVE-2026-27969
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:H/VI:H/VA:L/SC:L/SI:H/SA:H (CVSS_V4)
Published: 2026-02-27
Source: https://github.com/advisories/GHSA-r492-hjgh-c9gw
Type: github-advisory

## Affected
- Go: `vitess.io/vitess` — affected >=0.23.0-rc1 <0.23.3
- Go: `vitess.io/vitess` — affected >=0 <0.22.4

## Details
### Impact

Anyone with read/write access to the backup storage location (e.g. an S3 bucket) can manipulate backup manifest files so that files in the manifest — which may be files that they have also added to the manifest and backup contents — are written to any accessible location on restore. This is a common [Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal) security issue. This can be used to provide that attacker with unintended/unauthorized access to the production deployment environment — allowing them to access information available in that environment as well as run any additional arbitrary commands there.

### Patches

v23.0.3 and v22.0.4

### Resources

https://github.com/vitessio/vitess/pull/19470

## References
- https://github.com/vitessio/vitess/security/advisories/GHSA-r492-hjgh-c9gw
- https://nvd.nist.gov/vuln/detail/CVE-2026-27969
- https://github.com/vitessio/vitess/pull/19470
- https://github.com/vitessio/vitess/commit/c565cab615bc962bda061dcd645aa7506c59ca4a
- https://github.com/vitessio/vitess
- https://owasp.org/www-community/attacks/Path_Traversal
