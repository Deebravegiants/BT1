# [H] Moodle Denial of Service 

## Summary
Severity: High
Advisory: GHSA-66xp-28cq-mrf2
CVE: CVE-2020-25630
CWE: CWE-400
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-66xp-28cq-mrf2
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.2
- Packagist: `moodle/moodle` — affected >=3.8 <3.8.5
- Packagist: `moodle/moodle` — affected >=3.7 <3.7.8
- Packagist: `moodle/moodle` — affected >=3.5 <3.5.14

## Details
A vulnerability was found in Moodle where the decompressed size of zip files was not checked against available user quota before unzipping them, which could lead to a denial of service risk. This affects versions 3.9 to 3.9.1, 3.8 to 3.8.4, 3.7 to 3.7.7, 3.5 to 3.5.13 and earlier unsupported versions. Fixed in 3.9.2, 3.8.5, 3.7.8 and 3.5.14.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25630
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=410842
