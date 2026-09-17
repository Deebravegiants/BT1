# [C] Smarty3 Arbitrary PHP Code Execution

## Summary
Severity: Critical
Advisory: GHSA-6frx-2r5w-c524
CVE: CVE-2011-1028
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-6frx-2r5w-c524
Type: github-advisory

## Affected
- Packagist: `smarty/smarty` — affected >=0 <3.0.7

## Details
The `$smarty.template` variable in Smarty3 allows attackers to possibly execute arbitrary PHP code via the `sysplugins/smarty_internal_compile_private_special_variable.php` file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-1028
- https://github.com/smarty-php/smarty/commit/0154f17de2b2dd16ff9c016923015ac19af9c0cb
- https://github.com/smarty-php/smarty
- https://seclists.org/oss-sec/2011/q1/313
- https://security-tracker.debian.org/tracker/CVE-2011-1028
- https://web.archive.org/web/20110609032516/http://smarty-php.googlecode.com/svn/trunk/distribution/change_log.txt
- https://www.smarty.net/forums/viewtopic.php?t=18815
