# [H] Apache StreamPipes Improper Privilege Management vulnerability

## Summary
Severity: High
Advisory: GHSA-pm73-x2h5-cmj3
CVE: CVE-2023-31469
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-23
Source: https://github.com/advisories/GHSA-pm73-x2h5-cmj3
Type: github-advisory

## Affected
- Maven: `org.apache.streampipes:streampipes-parent` — affected >=0.69.0 <0.92.0

## Details
A REST interface in Apache StreamPipes (versions 0.69.0 to 0.91.0) was not properly restricted to admin-only access. This allowed a non-admin user with valid login credentials to elevate privileges beyond the initially assigned roles.
The issue is resolved by upgrading to StreamPipes 0.92.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31469
- https://github.com/apache/streampipes
- https://lists.apache.org/thread/c4y8kf9bzpf36v4bottfmd8tc9cxo19m
