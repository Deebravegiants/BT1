# [C] Dokku: OS Command Injection via app.json managed Cron

## Summary
Severity: Critical
Advisory: CVE-2026-54636
Aliases: GHSA-72vm-7pc2-x95w
CVSS: 9.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-54636
Type: osv

## Details
Dokku is a docker-powered PaaS. Prior to 0.38.7, the cron plugin utilizes commands in the app.json file to manage system cron running as the Dokku user. An app.json cron command utilizing special shell characters - including, but not limited to, > or ; - can break out of the Docker container and execute commands on the host as the Dokku user. This vulnerability is fixed in 0.38.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54636.json
- https://github.com/dokku/dokku/security/advisories/GHSA-72vm-7pc2-x95w
- https://nvd.nist.gov/vuln/detail/CVE-2026-54636
- https://github.com/dokku/dokku/pull/8672
