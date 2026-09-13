# [M] Windmill HTTP Request users.rs excessive authentication in github.com/windmill-labs/windmill

## Summary
Severity: Medium
Advisory: GHSA-g6q4-w3j3-jfc4
CVE: CVE-2024-8462
CWE: CWE-307
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-09-05
Source: https://github.com/advisories/GHSA-g6q4-w3j3-jfc4
Type: github-advisory

## Affected
- Go: `github.com/windmill-labs/windmill` — affected >=0

## Details
A vulnerability was found in Windmill 1.380.0. It has been classified as problematic. Affected is an unknown function of the file backend/windmill-api/src/users.rs of the component HTTP Request Handler. The manipulation leads to improper restriction of excessive authentication attempts. It is possible to launch the attack remotely. The complexity of an attack is rather high. The exploitability is told to be difficult. Upgrading to version 1.390.1 is able to address this issue. The patch is identified as acfe7786152f036f2476f93ab5536571514fa9e3. It is recommended to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8462
- https://github.com/windmill-labs/windmill/commit/acfe7786152f036f2476f93ab5536571514fa9e3
- https://github.com/windmill-labs/windmill
- https://github.com/windmill-labs/windmill/releases/tag/v1.390.1
- https://pkg.go.dev/vuln/GO-2024-3118
- https://vuldb.com/?ctiid.276630
- https://vuldb.com/?id.276630
- https://vuldb.com/?submit.401826
