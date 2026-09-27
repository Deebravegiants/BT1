# [C] Coolify has a Privilege Escalation - low privileged users can see and use admin invitation links

## Summary
Severity: Critical
Advisory: CVE-2025-64423
Aliases: GHSA-4fqm-797g-7m6j
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-05
Source: https://osv.dev/vulnerability/CVE-2025-64423
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. In Coolify versions up to and including v4.0.0-beta.434, a low privileged user (member) can see and use invitation links sent to an administrator. When they use the link before the legitimate recipient does, they are able to log in as an administrator, meaning they have successfully escalated their privileges. As of time of publication, it is unclear if a patch is available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64423.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-4fqm-797g-7m6j
- https://nvd.nist.gov/vuln/detail/CVE-2025-64423
