# [M] Grafana privilege escalation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fw9c-75hh-89p6
CVE: CVE-2023-4822
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2023-10-16
Source: https://github.com/advisories/GHSA-fw9c-75hh-89p6
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=0

## Details
Grafana is an open-source platform for monitoring and observability. The vulnerability impacts instances with several organizations, and allows a user with Organization Admin permissions in one organization to change the permissions associated with Organization Viewer, Organization Editor and Organization Admin roles in all organizations.

It also allows an Organization Admin to assign or revoke any permissions that they have to any user globally.

This means that any Organization Admin can elevate their own permissions in any organization that they are already a member of, or elevate or restrict the permissions of any other user.

The vulnerability does not allow a user to become a member of an organization that they are not already a member of, or to add any other users to an organization that the current user is not a member of.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-4822
- https://github.com/grafana/grafana
- https://grafana.com/security/security-advisories/cve-2023-4822
- https://security.netapp.com/advisory/ntap-20231103-0008
