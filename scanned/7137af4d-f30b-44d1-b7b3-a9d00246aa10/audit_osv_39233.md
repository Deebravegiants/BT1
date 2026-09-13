# [C] Faction: Unauthenticated Read, Modify, and Delete of Boilerplate Templates

## Summary
Severity: Critical
Advisory: CVE-2026-44668
Aliases: GHSA-7cv6-h22r-2qf2
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-44668
Type: osv

## Details
FACTION is a PenTesting Report Generation and Collaboration Framework. Prior to 1.8.3, AccessControlInterceptor, the authentication gate for all Struts2 actions, unconditionally calls invocation.invoke() without checking for a valid session. Four action methods in BoilerPlateConfig perform no local session check either, allowing an unauthenticated attacker to read, overwrite, deactivate, and permanently delete any boilerplate template in the system. This vulnerability is fixed in 1.8.3.

## References
- https://github.com/factionsecurity/faction/releases/tag/1.8.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44668.json
- https://github.com/factionsecurity/faction/security/advisories/GHSA-7cv6-h22r-2qf2
- https://nvd.nist.gov/vuln/detail/CVE-2026-44668
