# [C] Codiad Vulnerable to Shell Command Injection

## Summary
Severity: Critical
Advisory: GHSA-jccv-3h4x-35mv
CVE: CVE-2017-11366
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-jccv-3h4x-35mv
Type: github-advisory

## Affected
- Packagist: `codiad/codiad` — affected >=0 <2.8.3

## Details
components/filemanager/class.filemanager.php in Codiad before 2.8.3 is vulnerable to remote command execution because shell commands can be embedded in parameter values, as demonstrated by `search_file_type`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11366
- https://github.com/Codiad/Codiad/issues/1011
- https://github.com/Codiad/Codiad/pull/1013
- https://github.com/Codiad/Codiad/pull/1013/commits/b3645b4c6718cef6de7003f41aafe7bfcc0395d1
- https://github.com/Codiad/Codiad/commit/ca5089eeba42d16ce3a7f86be628ac7750780111
- https://github.com/Codiad/Codiad
- http://www.jianshu.com/p/41ac7ac2a7af
