# [M] decolua 9router vulnerable to authorization bypass

## Summary
Severity: Medium
Advisory: GHSA-xrrh-p7f2-27vm
CVE: CVE-2026-5842
CWE: CWE-285
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-xrrh-p7f2-27vm
Type: github-advisory

## Affected
- npm: `9router` — affected >=0 <0.3.75

## Details
A security vulnerability has been detected in decolua 9router up to 0.3.47. The impacted element is an unknown function of the file /api of the component Administrative API Endpoint. The manipulation leads to authorization bypass. The attack is possible to be carried out remotely. The exploit has been disclosed publicly and may be used. Upgrading to version 0.3.75 is sufficient to resolve this issue. It is suggested to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5842
- https://github.com/decolua/9router/issues/431
- https://github.com/decolua/9router/issues/431#issuecomment-4140163867
- https://github.com/decolua/9router
- https://github.com/decolua/9router/releases/tag/v0.3.75
- https://github.com/deepcat1337/Free_Api_Exploit/tree/main
- https://vuldb.com/submit/790003
- https://vuldb.com/vuln/356298
- https://vuldb.com/vuln/356298/cti
