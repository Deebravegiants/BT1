# [M] Moodle Arbitrary Redirect

## Summary
Severity: Medium
Advisory: GHSA-h798-h7ff-93xv
CVE: CVE-2015-3175
CWE: CWE-601
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-h798-h7ff-93xv
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0
- Packagist: `moodle/moodle` — affected >=2.6.0 <2.6.11
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.8
- Packagist: `moodle/moodle` — affected >=2.8.0 <2.8.6

## Details
Multiple open redirect vulnerabilities in Moodle through 2.5.9, 2.6.x before 2.6.11, 2.7.x before 2.7.8, and 2.8.x before 2.8.6 allow remote attackers to redirect users to arbitrary web sites and conduct phishing attacks via vectors involving an error page that links to a URL from an HTTP Referer header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3175
- https://github.com/moodle/moodle/commit/b2687a055dc990ca86ddce178d5aee3fb1df644a
- https://github.com/moodle/moodle/commit/db200a8e9f88c8c4a2141ac264062dca74ee2f29
- https://github.com/moodle/moodle/commit/dd0607b7bbaff38cc62e4d00658c02da3fdbb4c8
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=313682
- https://web.archive.org/web/20201030042703/http://www.securitytracker.com/id/1032358
- https://web.archive.org/web/20210122155902/http://www.securityfocus.com/bid/74720
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-49179
- http://openwall.com/lists/oss-security/2015/05/18/1
