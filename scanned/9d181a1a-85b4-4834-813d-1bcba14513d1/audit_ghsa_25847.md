# [H] Moodle Blind SQL injection possible via MNet authentication

## Summary
Severity: High
Advisory: GHSA-rvmc-8gmg-ggqr
CVE: CVE-2021-32474
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-12
Source: https://github.com/advisories/GHSA-rvmc-8gmg-ggqr
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.10 <3.10.4
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.7
- Packagist: `moodle/moodle` — affected >=3.8 <3.8.9
- Packagist: `moodle/moodle` — affected >=3.5 <3.5.18

## Details
An SQL injection risk existed on sites with MNet enabled and configured, via an XML-RPC call from the connected peer host. Note that this required site administrator access or access to the keypair. Moodle 3.10 to 3.10.3, 3.9 to 3.9.6, 3.8 to 3.8.8, 3.5 to 3.5.17 and earlier unsupported versions are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32474
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=422308
