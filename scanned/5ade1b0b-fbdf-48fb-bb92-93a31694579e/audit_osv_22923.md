# [M] CVE-2022-41230

## Summary
Severity: Medium
Advisory: CVE-2022-41230
Aliases: GHSA-3jp6-q9cg-rvgj
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-09-21
Source: https://osv.dev/vulnerability/CVE-2022-41230
Type: osv

## Details
Jenkins Build-Publisher Plugin 1.22 and earlier does not perform a permission check in an HTTP endpoint, allowing attackers with Overall/Read permission to obtain names and URLs of Jenkins servers that the plugin is configured to publish builds to, as well as builds pending for publication to those Jenkins servers.

## References
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-1994
