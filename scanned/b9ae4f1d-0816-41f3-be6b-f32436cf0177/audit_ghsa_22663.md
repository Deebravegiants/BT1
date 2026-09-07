# [M] Moodle Stored HTML in assignment submission comments allowed links to be opened directly

## Summary
Severity: Medium
Advisory: GHSA-3fj7-9j8m-7r8g
CVE: CVE-2019-3850
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3fj7-9j8m-7r8g
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <3.1.17
- Packagist: `moodle/moodle` — affected >=3.2.0 <3.4.8
- Packagist: `moodle/moodle` — affected >=3.5.0 <3.5.5
- Packagist: `moodle/moodle` — affected >=3.6.0 <3.6.3

## Details
A vulnerability was found in moodle before versions 3.6.3, 3.5.5, 3.4.8 and 3.1.17. Links within assignment submission comments would open directly (in the same window). Although links themselves may be valid, opening within the same window and without the no-referrer header policy made them more susceptible to exploits.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3850
- https://github.com/moodle/moodle/commit/1fc481dd7b09e08e85824c1fe6733b303a36bdce
- https://github.com/moodle/moodle/commit/772c908d40a944efd91d897d524b255626d330d4
- https://github.com/moodle/moodle/commit/907b377e51c32ea37feef53e10684b504e103273
- https://github.com/moodle/moodle/commit/d3f2f990dd3c5d4e6073a77154c6423d1c304647
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3850
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=384013#p1547745
