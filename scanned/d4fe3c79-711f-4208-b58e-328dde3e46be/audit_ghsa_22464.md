# [H] CakePHP might allow remote attackers to bypass CSRF protection mechanism via the _method parameter

## Summary
Severity: High
Advisory: GHSA-556q-h4vr-pgh2
CVE: CVE-2015-8379
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-556q-h4vr-pgh2
Type: github-advisory

## Affected
- Packagist: `cakephp/cakephp` — affected >=2.0.0-alpha <3.1.5

## Details
CakePHP 2.x and 3.x before 3.1.5 might allow remote attackers to bypass the CSRF protection mechanism via the `_method` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8379
- https://github.com/cakephp/cakephp/commit/0f818a23a876c01429196bf7623e1e94a50230f0
- https://github.com/cakephp/cakephp
- http://bakery.cakephp.org/2015/11/29/cakephp_315_released.html
- http://blog.mindedsecurity.com/2016/01/request-parameter-method-may-lead-to.html
- http://karmainsecurity.com/KIS-2016-01
- http://packetstormsecurity.com/files/135301/CakePHP-3.2.0-CSRF-Bypass.html
- http://seclists.org/fulldisclosure/2016/Jan/42
- http://www.securityfocus.com/archive/1/537317/100/0/threaded
