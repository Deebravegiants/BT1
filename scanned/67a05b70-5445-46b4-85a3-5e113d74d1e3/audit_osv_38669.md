# [C] mdserver-web: Missing Authorization and Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')

## Summary
Severity: Critical
Advisory: CVE-2026-41315
Aliases: GHSA-3h92-g9hr-xc25
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-41315
Type: osv

## Details
mdserver-web is a simple Linux panel. From 0.18.0 to 0.18.4, mdserver-web has a front-end unauthorized remote command execution vulnerability. Due to the lack of authentication on the /modify_crond and /start_task interfaces, it is possible to modify the default built-in scheduled tasks and start them, achieving RCE.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41315.json
- https://github.com/midoks/mdserver-web/security/advisories/GHSA-3h92-g9hr-xc25
- https://nvd.nist.gov/vuln/detail/CVE-2026-41315
