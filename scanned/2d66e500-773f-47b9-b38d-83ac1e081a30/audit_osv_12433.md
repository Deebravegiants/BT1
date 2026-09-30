# [M] CVE-2018-1193

## Summary
Severity: Medium
Advisory: CVE-2018-1193
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-05-23
Source: https://osv.dev/vulnerability/CVE-2018-1193
Type: osv

## Details
Cloud Foundry routing-release, versions prior to 0.175.0, lacks sanitization for user-provided X-Forwarded-Proto headers. A remote user can set the X-Forwarded-Proto header in a request to potentially bypass an application requirement to only respond over secure connections.

## References
- https://www.cloudfoundry.org/blog/cve-2018-1193/
