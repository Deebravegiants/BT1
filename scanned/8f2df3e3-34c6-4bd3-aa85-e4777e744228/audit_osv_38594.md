# [M] mailcow: dockerized missing authorization on Forwarding Hosts delete action

## Summary
Severity: Medium
Advisory: CVE-2026-40874
Aliases: GHSA-jjxh-rm7p-hjc3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40874
Type: osv

## Details
mailcow: dockerized is an open source groupware/email suite based on docker. In versions prior to 2026-03b, no administrator verification takes place when deleting Forwarding Hosts with `/api/v1/delete/fwdhost`. Any authenticated user can call this API. Checks are only applied for edit/add actions, but deletion can still significantly disrupt the mail service. Version 2026-03b fixes the vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40874.json
- https://github.com/mailcow/mailcow-dockerized/security/advisories/GHSA-jjxh-rm7p-hjc3
- https://nvd.nist.gov/vuln/detail/CVE-2026-40874
