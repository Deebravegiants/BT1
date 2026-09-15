# [M] Matrix Sydent mishandles emails

## Summary
Severity: Medium
Advisory: GHSA-q9h8-gpw5-c95c
CVE: CVE-2019-11340
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q9h8-gpw5-c95c
Type: github-advisory

## Affected
- PyPI: `matrix-sydent` — affected >=0 <1.0.2

## Details
util/emailutils.py in Matrix Sydent before 1.0.2 mishandles registration restrictions that are based on e-mail domain, if the allowed_local_3pids option is enabled. This occurs because of potentially unwanted behavior in Python, in which an email.utils.parseaddr call on user@bad.example.net@good.example.com returns the user@bad.example.net substring.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11340
- https://github.com/matrix-org/sydent/commit/4e1cfff53429c49c87d5c457a18ed435520044fc
- https://github.com/matrix-org/sydent/compare/7c002cd...09278fb
- https://matrix.org/blog/2019/04/18/security-update-sydent-1-0-2
- https://twitter.com/matrixdotorg/status/1118934335963500545
