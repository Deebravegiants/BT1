# [M] Moodle XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qrcj-6fjw-3h9h
CVE: CVE-2019-3847
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-qrcj-6fjw-3h9h
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.6.0 <3.6.3
- Packagist: `moodle/moodle` — affected >=3.5.0 <3.5.5
- Packagist: `moodle/moodle` — affected >=3.2.0 <3.4.8
- Packagist: `moodle/moodle` — affected >=0 <3.1.17

## Details
A vulnerability was found in moodle before versions 3.6.3, 3.5.5, 3.4.8 and 3.1.17. Users with the "login as other users" capability (such as administrators/managers) can access other users' Dashboards, but the JavaScript those other users may have added to their Dashboard was not being escaped when being viewed by the user logging in on their behalf.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3847
- https://github.com/moodle/moodle/commit/070f24d006eab6b958eb083530de159b43c538ed
- https://github.com/moodle/moodle/commit/93dda3bfd3caaaa8d23fe8ede543f27ef774958d
- https://github.com/moodle/moodle/commit/a37e26d2efe1ca0e4d8d69c611a748af35b33674
- https://github.com/moodle/moodle/commit/e836242e1c04cd62d0afa4a790074fd245628e7a
- https://github.com/moodle/moodle/commit/ec3b63c772d6448765c68268234cf36c1a91bcac
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3847
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=384010#p1547742
- https://web.archive.org/web/20200227082922/http://www.securityfocus.com/bid/107489
