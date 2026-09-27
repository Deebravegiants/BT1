# [M] Smarty Does Not Consider Umask Values When Setting Permissions

## Summary
Severity: Medium
Advisory: GHSA-6m9f-8vwq-97pm
CVE: CVE-2009-5054
CWE: CWE-281
Ecosystem: Packagist
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-6m9f-8vwq-97pm
Type: github-advisory

## Affected
- Packagist: `smarty/smarty` — affected >=0 <3.0.0-beta4

## Details
Smarty before 3.0.0 beta 4 does not consider the umask value when setting the permissions of files, which might allow attackers to bypass intended access restrictions via standard filesystem operations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-5054
- https://github.com/smarty-php/smarty
- https://web.archive.org/web/20101116174040/http://smarty-php.googlecode.com/svn/trunk/distribution/change_log.txt
