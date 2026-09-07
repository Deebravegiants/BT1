# [M] Moodle Open Redirect in Calendar Set Page

## Summary
Severity: Medium
Advisory: GHSA-jcrj-x36p-h9f6
CVE: CVE-2011-4582
CWE: CWE-601
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-jcrj-x36p-h9f6
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.1 <2.1.3

## Details
Open redirect vulnerability in the Calendar set page in Moodle 2.1.x before 2.1.3 allows remote authenticated users to redirect users to arbitrary web sites and conduct phishing attacks via a redirection URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4582
- https://github.com/moodle/moodle/commit/0d2672748c00181d9cdae2aabbab916cbd64c47d
- https://github.com/moodle/moodle/commit/21e7d4c5fc9cc5df54c9c7d82190f1339d163a9e
- https://github.com/moodle/moodle/commit/7f422374c101dcb0affdd5127b855671af4f3748
- https://github.com/moodle/moodle/commit/eb59a448f7879d69b21fcde7f1fcddd69655e045
- https://bugzilla.redhat.com/show_bug.cgi?id=761248
- https://github.com/moodle/moodle
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-28720&sr=1
- http://moodle.org/mod/forum/discuss.php?d=191748
