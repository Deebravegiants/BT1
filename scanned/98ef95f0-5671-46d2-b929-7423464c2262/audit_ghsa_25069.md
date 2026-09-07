# [M] MantisBT vulnerable to CSRF and Open Redirect attacks

## Summary
Severity: Medium
Advisory: GHSA-9x76-mp7r-2xc5
CVE: CVE-2017-7620
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9x76-mp7r-2xc5
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <1.3.11
- Packagist: `mantisbt/mantisbt` — affected >=2.0.0 <2.3.3
- Packagist: `mantisbt/mantisbt` — affected >=2.4.0 <2.4.1

## Details
MantisBT before 1.3.11, 2.x before 2.3.3, and 2.4.x before 2.4.1 omits a backslash check in string_api.php and consequently has conflicting interpretations of an initial \/ substring as introducing either a local pathname or a remote hostname, which leads to (1) arbitrary Permalink Injection via CSRF attacks on a permalink_page.php?url= URI and (2) an open redirect via a login_page.php?return= URI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7620
- https://github.com/mantisbt/mantisbt/commit/2d2309a384bcd9d4b6d7d2928e8ded2c46d2d7b0
- https://github.com/mantisbt/mantisbt/commit/8b6787c8d321ee0ced5fb74ac3f34b67b4b7b26c
- https://github.com/mantisbt/mantisbt/commit/c4f50e5df6b189abb1d717a5f7dbab5cbfef8165
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=22702
- https://mantisbt.org/bugs/view.php?id=22816
- https://www.exploit-db.com/exploits/42043
- http://hyp3rlinx.altervista.org/advisories/MANTIS-BUG-TRACKER-CSRF-PERMALINK-INJECTION.txt
