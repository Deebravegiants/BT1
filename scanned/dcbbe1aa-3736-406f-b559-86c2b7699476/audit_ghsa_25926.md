# [H] Moodle denial-of-service risk in the draft files area

## Summary
Severity: High
Advisory: GHSA-4qxc-qxrp-33cw
CVE: CVE-2021-32476
CWE: CWE-400, CWE-770
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-03-12
Source: https://github.com/advisories/GHSA-4qxc-qxrp-33cw
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.10 <3.10.4
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.7
- Packagist: `moodle/moodle` — affected >=3.8 <3.8.9
- Packagist: `moodle/moodle` — affected >=3.5.17 <3.5.18

## Details
A denial-of-service risk was identified in the draft files area, due to it not respecting user file upload limits. Moodle versions 3.10 to 3.10.3, 3.9 to 3.9.6, 3.8 to 3.8.8, 3.5 to 3.5.17 and earlier unsupported versions are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32476
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=422310
