# [H] Improper certificate validation in em-imap

## Summary
Severity: High
Advisory: GHSA-4f68-49qq-h392
CVE: CVE-2020-13163
CWE: CWE-295
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-05-24
Source: https://github.com/advisories/GHSA-4f68-49qq-h392
Type: github-advisory

## Affected
- RubyGems: `em-imap` — affected >=0

## Details
em-imap 0.5 and earlier use the library eventmachine in an insecure way that allows an attacker to perform a man-in-the-middle attack against users of the library. The hostname in a TLS server certificate is not verified.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13163
- https://github.com/ConradIrwin/em-imap/issues/25
- https://github.com/ConradIrwin/em-imap
- https://securitylab.github.com/advisories/GHSL-2020-095-conradirwin-em-imap
