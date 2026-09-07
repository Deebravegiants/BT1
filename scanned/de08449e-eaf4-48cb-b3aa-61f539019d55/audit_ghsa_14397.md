# [M] Moodle has a Hidden Functionality vulnerability

## Summary
Severity: Medium
Advisory: GHSA-j9cw-5cpj-9qj5
CVE: CVE-2021-36403
CWE: CWE-912
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-03-07
Source: https://github.com/advisories/GHSA-j9cw-5cpj-9qj5
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.11.0-beta <3.11.1
- Packagist: `moodle/moodle` — affected >=3.10.0-beta <3.10.5
- Packagist: `moodle/moodle` — affected >=0 <3.9.8

## Details
In Moodle, in some circumstances, email notifications of messages could have the link back to the original message hidden by HTML, which may pose a phishing risk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36403
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=424809
