# [M] pwn.college DOJO vulnerable to sandbox escape leading to arbitrary javascript execution

## Summary
Severity: Medium
Advisory: CVE-2026-25117
Aliases: GHSA-wvcf-9xm8-7mrg
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N)
Published: 2026-01-29
Source: https://osv.dev/vulnerability/CVE-2026-25117
Type: osv

## Details
pwn.college DOJO is an education platform for learning cybersecurity. Prior to commit e33da14449a5abcff507e554f66e2141d6683b0a, missing sandboxing on `/workspace/*` routes allows challenge authors to inject arbitrary javascript which runs on the same origin as `http[:]//dojo[.]website`. This is a sandbox escape leading to arbitrary javascript execution as the dojo's origin. A challenge author can craft a page that executes any dangerous actions that the user could. Version e33da14449a5abcff507e554f66e2141d6683b0a patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25117.json
- https://github.com/pwncollege/dojo/security/advisories/GHSA-wvcf-9xm8-7mrg
- https://nvd.nist.gov/vuln/detail/CVE-2026-25117
- https://github.com/pwncollege/dojo/commit/e33da14449a5abcff507e554f66e2141d6683b0a
