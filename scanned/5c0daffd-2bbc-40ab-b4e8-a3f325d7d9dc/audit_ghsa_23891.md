# [M] Moodle Cross-site Scripting vulnerability in the KSES text cleaning filter 

## Summary
Severity: Medium
Advisory: GHSA-3gm8-32vv-q8mp
CVE: CVE-2010-2230
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3gm8-32vv-q8mp
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <1.8.13
- Packagist: `moodle/moodle` — affected >=1.9.0 <1.9.9

## Details
The KSES text cleaning filter in lib/weblib.php in Moodle before 1.8.13 and 1.9.x before 1.9.9 does not properly handle vbscript URIs, which allows remote authenticated users to conduct cross-site scripting (XSS) attacks via HTML input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-2230
- https://github.com/moodle/moodle/commit/704c5dfed4f4531b6d74d19cfad573984e74885e
- https://bugzilla.redhat.com/show_bug.cgi?id=605809
- https://github.com/moodle/moodle
- https://web.archive.org/web/20100621005117/http://secunia.com/advisories/40248
- https://web.archive.org/web/20100711044720/http://secunia.com/advisories/40352
- http://cvs.moodle.org/moodle/lib/weblib.php?r1=1.812.2.114&r2=1.812.2.115
- http://cvs.moodle.org/moodle/lib/weblib.php?r1=1.970.2.171&r2=1.970.2.172
- http://docs.moodle.org/en/Moodle_1.8.13_release_notes
- http://docs.moodle.org/en/Moodle_1.9.9_release_notes
- http://lists.fedoraproject.org/pipermail/package-announce/2010-June/043285.html
- http://lists.fedoraproject.org/pipermail/package-announce/2010-June/043291.html
- http://lists.fedoraproject.org/pipermail/package-announce/2010-June/043340.html
- http://lists.opensuse.org/opensuse-security-announce/2010-08/msg00001.html
- http://moodle.org/mod/forum/discuss.php?d=152368
- http://tracker.moodle.org/browse/MDL-22042
- http://www.openwall.com/lists/oss-security/2010/06/21/2
- http://www.vupen.com/english/advisories/2010/1530
- http://www.vupen.com/english/advisories/2010/1571
