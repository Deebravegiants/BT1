# [M] Pagekit User enumeration

## Summary
Severity: Medium
Advisory: GHSA-jh2j-7248-9p3c
CVE: CVE-2019-16669
CWE: CWE-203
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jh2j-7248-9p3c
Type: github-advisory

## Affected
- Packagist: `pagekit/pagekit` — affected 1.0.17

## Details
The Reset Password feature in Pagekit 1.0.17 gives a different response depending on whether the e-mail address of a valid user account is entered, which might make it easier for attackers to enumerate accounts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16669
- https://github.com/pagekit/pagekit/issues/935
- https://github.com/pagekit/pagekit
