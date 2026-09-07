# [H] ThinkPHP Remote Code Execution (RCE) vulnerability

## Summary
Severity: High
Advisory: GHSA-75jp-87w2-c6x2
CVE: CVE-2021-44892
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-11
Source: https://github.com/advisories/GHSA-75jp-87w2-c6x2
Type: github-advisory

## Affected
- Packagist: `topthink/framework` — affected >=0

## Details
A Remote Code Execution (RCE) vulnerability exists in ThinkPHP 3.x.x via value[_filename] in index.php, which could let a malicious user obtain server control privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44892
- https://github.com/Stakcery/Web-Security/issues/1
- https://github.com/top-think/framework
