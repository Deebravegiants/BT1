# [C] Authenticated users of Combodo iTop can take over any account

## Summary
Severity: Critical
Advisory: CVE-2022-39214
Aliases: GHSA-vj96-j84g-jhx4
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2023-03-14
Source: https://osv.dev/vulnerability/CVE-2022-39214
Type: osv

## Details
Combodo iTop is an open source, web-based IT service management platform. Prior to versions 2.7.8 and 3.0.2-1, a user who can log in on iTop is able to take over any account just by knowing the account's username. This issue is fixed in versions 2.7.8 and 3.0.2-1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39214.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-vj96-j84g-jhx4
- https://nvd.nist.gov/vuln/detail/CVE-2022-39214
- https://github.com/Combodo/iTop/commit/4c1df9927d1dc6b0181ee20721f93346def026fd
- https://github.com/Combodo/iTop/commit/bdebea62b642622ed71410b26c81e8537e6e58fa
