# [H] MODX Revolution Incorrect Access Control vulnerability

## Summary
Severity: High
Advisory: GHSA-m899-6mh4-mpc5
CVE: CVE-2018-1000207
CWE: CWE-732
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-m899-6mh4-mpc5
Type: github-advisory

## Affected
- Packagist: `modx/revolution` — affected >=0 <2.7.0

## Details
MODX Revolution version <=2.6.4 contains a Incorrect Access Control vulnerability in Filtering user parameters before passing them into phpthumb class that can result in Creating file with custom a filename and content. This attack appear to be exploitable via Web request. This vulnerability appears to have been fixed in commit 06bc94257408f6a575de20ddb955aca505ef6e68.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000207
- https://github.com/modxcms/revolution/pull/13979
- https://github.com/modxcms/revolution/commit/06bc94257408f6a575de20ddb955aca505ef6e68
- https://github.com/a2u/CVE-2018-1000207
- https://github.com/modxcms/revolution
- https://rudnkh.me/posts/critical-vulnerability-in-modx-revolution-2-6-4
