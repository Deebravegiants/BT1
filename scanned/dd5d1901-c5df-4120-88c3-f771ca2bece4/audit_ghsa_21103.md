# [M] FlyteAdmin Insufficient AccessToken Expiration Check

## Summary
Severity: Medium
Advisory: GHSA-qwrj-9hmp-gpxh
CVE: CVE-2022-31145
CWE: CWE-298, CWE-613
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-07-15
Source: https://github.com/advisories/GHSA-qwrj-9hmp-gpxh
Type: github-advisory

## Affected
- Go: `github.com/flyteorg/flyteadmin` — affected >=0 <1.1.31

## Details
### Impact
Authenticated users using an external identity provider can continue to use Access Tokens and ID Tokens even after they expire.
Using flyteadmin as the OAuth2 Authorization Server is unaffected by this issue.

### Patches
1.1.30

### Workarounds
Rotating signing keys immediately will:
* Invalidate all open sessions,
* Force all users to attempt to obtain new tokens.

Continue to rotate keys until flyteadmin has been upgraded,

Hide flyteadmin deployment ingress url from the internet.

### References
https://github.com/flyteorg/flyteadmin/pull/455

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [flyte repo](https://github.com/flyteorg/flyte/issues)
* Email us at [flyte](mailto:admin@flyte.org)

## References
- https://github.com/flyteorg/flyteadmin/security/advisories/GHSA-qwrj-9hmp-gpxh
- https://nvd.nist.gov/vuln/detail/CVE-2022-31145
- https://github.com/flyteorg/flyteadmin/pull/455
- https://github.com/flyteorg/flyteadmin/commit/a1ec282d02706e074bc4986fd0412e5da3b9d00a
- https://github.com/flyteorg/flyteadmin
- https://github.com/flyteorg/flyteadmin/releases/tag/v1.1.31
- https://pkg.go.dev/vuln/GO-2022-0519
