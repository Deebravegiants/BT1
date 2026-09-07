# [M] Moodle does not provide charset information in HTTP headers

## Summary
Severity: Medium
Advisory: GHSA-crcq-pw8h-9xwf
CVE: CVE-2014-9059
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-crcq-pw8h-9xwf
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.5.9
- Packagist: `moodle/moodle` — affected >=2.6.0 <2.6.6
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.3

## Details
lib/setup.php in Moodle through 2.4.11, 2.5.x before 2.5.9, 2.6.x before 2.6.6, and 2.7.x before 2.7.3 does not provide charset information in HTTP headers, which might allow remote attackers to conduct cross-site scripting (XSS) attacks via UTF-7 characters during interaction with AJAX scripts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-9059
- https://github.com/moodle/moodle/commit/0a0145c5e8041aadeff303a9f9984c86706b4e42
- https://github.com/moodle/moodle/commit/293e4bbcb71f0a801c2539ea051c58688314b23a
- https://github.com/moodle/moodle/commit/3c98b7a5ad1bb596a738e550fc3bf966d6415fe0
- https://github.com/moodle/moodle/commit/ac6e453d11024bf6ad99ada1bfc641c6b91ebed6
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=275146
- https://web.archive.org/web/20150914064838/http://www.securitytracker.com/id/1031215
- https://web.archive.org/web/20200229043651/http://www.securityfocus.com/bid/71133
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-47966
- http://www.securitytracker.com/id/1031215
