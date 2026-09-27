# [M] Authorino Uncontrolled Resource Consumption vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r8xr-pgv5-gxw3
CVE: CVE-2025-25207
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-06-09
Source: https://github.com/advisories/GHSA-r8xr-pgv5-gxw3
Type: github-advisory

## Affected
- Go: `github.com/kuadrant/authorino` — affected >=0

## Details
The Authorino service in the Red Hat Connectivity Link is the authorization service for zero trust API security. Authorino allows the users with developer persona to add callbacks to be executed to HTTP endpoints once the authorization process is completed. It was found that an attacker with developer persona access can add a large number of those callbacks to be executed by Authorino and as the authentication policy is enforced by a single instance of the service, this leada to a Denial of Service in Authorino while processing the post-authorization callbacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-25207
- https://access.redhat.com/security/cve/CVE-2025-25207
- https://bugzilla.redhat.com/show_bug.cgi?id=2347421
- https://github.com/Kuadrant/authorino
