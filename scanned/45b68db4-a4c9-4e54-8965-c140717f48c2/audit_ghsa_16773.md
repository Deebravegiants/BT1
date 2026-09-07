# [H] Moodle ReCAPTCHA can be bypassed on the login page

## Summary
Severity: High
Advisory: GHSA-gwf6-q6c2-94p3
CVE: CVE-2024-34009
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-05-31
Source: https://github.com/advisories/GHSA-gwf6-q6c2-94p3
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.3.0 <4.3.4

## Details
Insufficient checks whether ReCAPTCHA was enabled made it possible to bypass the checks on the login page. This did not affect other pages where ReCAPTCHA is utilized.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34009
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=458398
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-81463
