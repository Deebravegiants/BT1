# [M] Moodle Unsanitized HTML in site log for config_log_created

## Summary
Severity: Medium
Advisory: GHSA-vvh5-7v3m-j3mj
CVE: CVE-2024-34006
CWE: CWE-838
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-05-31
Source: https://github.com/advisories/GHSA-vvh5-7v3m-j3mj
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.3.0 <4.3.4
- Packagist: `moodle/moodle` — affected >=4.2.0 <4.2.7
- Packagist: `moodle/moodle` — affected >=0 <4.1.10

## Details
The site log report required additional encoding of event descriptions to ensure any HTML in the content is displayed in plaintext instead of being rendered.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34006
- https://github.com/moodle/moodle/commit/cd85e090f3feb06e6eff65d1499a67353d82d3cb
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=458395
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-80585
