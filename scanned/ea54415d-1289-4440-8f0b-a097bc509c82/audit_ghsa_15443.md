# [H] Juju's unprivileged user running on charm node can leak any secret or relation data accessible to the local charm

## Summary
Severity: High
Advisory: GHSA-6vjm-54vp-mxhx
CWE: CWE-209, CWE-269, CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-6vjm-54vp-mxhx
Type: github-advisory

## Affected
- Go: `github.com/juju/juju` — affected >=0 <2.9.50
- Go: `github.com/juju/juju` — affected >=3.0.0 <3.1.9
- Go: `github.com/juju/juju` — affected >=3.2.0 <3.3.6
- Go: `github.com/juju/juju` — affected >=3.4.0 <3.4.5
- Go: `github.com/juju/juju` — affected >=3.5.0 <3.5.3

## Details
An issue was discovered in Juju that resulted in the leak of the sensitive context ID, which allows a local unprivileged attacker to access other sensitive data or relation accessible to the local charm. A potential exploit where a user can run a bash loop attempting to execute hook tools. If running while another hook is executing, we log an error with the context ID, making it possible for the user to then use that ID in a following call successfully. This means an unprivileged user can access anything available via a hook tool such as config, relation data and secrets.

## References
- https://github.com/juju/juju/security/advisories/GHSA-6vjm-54vp-mxhx
- https://nvd.nist.gov/vuln/detail/CVE-2024-6984
- https://github.com/juju/juju/commit/da929676853092a29ddf8d589468cf85ba3efaf2
- https://github.com/juju/juju
- https://pkg.go.dev/vuln/GO-2024-3010
- https://pkg.go.dev/vuln/GO-2024-3040
