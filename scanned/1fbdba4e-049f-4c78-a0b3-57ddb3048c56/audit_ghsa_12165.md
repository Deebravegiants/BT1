# [M] Cloudfoundry UAA has logic error in the token revocation endpoint implementation

## Summary
Severity: Medium
Advisory: GHSA-6wcw-r64p-qrrw
CVE: CVE-2026-22723
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-6wcw-r64p-qrrw
Type: github-advisory

## Affected
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=77.30.0 <78.8.0

## Details
Inappropriate user token revocation due to a logic error in the token revocation endpoint implementation in Cloudfoundry UAA v77.30.0 to v78.7.0 and in Cloudfoundry Deployment v48.7.0 to v54.10.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22723
- https://github.com/cloudfoundry/uaa/commit/74c88235b5bc6e61752624700e91f61fd724dfcd
- https://github.com/cloudfoundry/uaa
- https://github.com/cloudfoundry/uaa/releases/tag/v78.8.0
- https://www.cloudfoundry.org/blog/cve-2026-22723-uaa-user-token-revocation
