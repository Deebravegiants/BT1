# [C] Craft CMS Remote Code Injection

## Summary
Severity: Critical
Advisory: GHSA-x2j7-6hxm-87p3
CVE: CVE-2021-27903
CWE: CWE-74, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-07-02
Source: https://github.com/advisories/GHSA-x2j7-6hxm-87p3
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=0 <3.6.7

## Details
An issue was discovered in Craft CMS before 3.6.7. In some circumstances, a potential Remote Code Execution vulnerability existed on sites that did not restrict administrative changes (if an attacker were somehow able to hijack an administrator's session).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27903
- https://github.com/craftcms/cms/commit/c17728fa0bec11d3b82c34defe0930ed409aec38
- https://github.com/craftcms/cms/blob/develop/CHANGELOG.md#367---2021-02-23
- https://github.com/craftcms/cms/blob/develop/CHANGELOG.md#security
