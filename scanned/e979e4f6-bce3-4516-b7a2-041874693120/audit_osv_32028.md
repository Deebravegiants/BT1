# [M] Coolify Vulnerable to GitHub / GitLab OAuth Secrets Leak

## Summary
Severity: Medium
Advisory: CVE-2025-22607
Aliases: GHSA-8w24-gfgq-jg72
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2025-01-24
Source: https://osv.dev/vulnerability/CVE-2025-22607
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to version 4.0.0-beta.361, the missing authorization allows any authenticated user to fetch the details page for any GitHub / GitLab configuration on a Coolify instance by only knowing the UUID of the model. This exposes the "client id", "client secret" and "webhook secret." Version 4.0.0-beta.361 fixes this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22607.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-8w24-gfgq-jg72
- https://nvd.nist.gov/vuln/detail/CVE-2025-22607
