# [C] WeGIA Vulnerable to Authentication Bypass via `extract($_REQUEST)`

## Summary
Severity: Critical
Advisory: CVE-2026-28411
Aliases: GHSA-g7r9-hxc8-8vh7
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-28411
Type: osv

## Details
WeGIA is a web manager for charitable institutions. Prior to version 3.6.5, an unsafe use of the `extract()` function on the `$_REQUEST` superglobal allows an unauthenticated attacker to overwrite local variables in multiple PHP scripts. This vulnerability can be leveraged to completely bypass authentication checks, allowing unauthorized access to administrative and protected areas of the WeGIA application. Version 3.6.5 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28411.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-g7r9-hxc8-8vh7
- https://nvd.nist.gov/vuln/detail/CVE-2026-28411
