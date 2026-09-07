# [M] Moodle's feedback response viewing and deletions did not respect Separate Groups mode

## Summary
Severity: Medium
Advisory: GHSA-pxg4-xjp7-w9c5
CVE: CVE-2025-26526
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-02-24
Source: https://github.com/advisories/GHSA-pxg4-xjp7-w9c5
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.2
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.6
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.10
- Packagist: `moodle/moodle` — affected >=0 <4.1.16

## Details
Separate Groups mode restrictions were not factored into permission checks before allowing viewing or deletion of responses in Feedback 
activities.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-26526
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=466142
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-79976
