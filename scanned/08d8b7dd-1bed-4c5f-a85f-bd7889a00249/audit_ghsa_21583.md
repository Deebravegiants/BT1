# [M] Tribal Systems Zenario CMS vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-f92p-f8r2-c87q
CVE: CVE-2020-36608
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-03
Source: https://github.com/advisories/GHSA-f92p-f8r2-c87q
Type: github-advisory

## Affected
- Packagist: `tribalsystems/zenario` — affected >=0 <8.5.51340

## Details
A vulnerability has been found in Tribal Systems Zenario CMS prior to version 8.5.51340. Affected by this issue is some unknown functionality of the file `admin_organizer.js` of the component `Error Log Module`. The manipulation leads to cross site scripting. The attack may be launched remotely. The issue is patched in version 8.5.51340.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36608
- https://github.com/TribalSystems/Zenario/commit/dfd0afacb26c3682a847bea7b49ea440b63f3baa
- https://github.com/TribalSystems/Zenario
- https://vuldb.com/?id.212816
