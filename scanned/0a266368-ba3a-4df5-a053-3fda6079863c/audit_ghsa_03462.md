# [M] Improper Certificate Validation in TweetStream

## Summary
Severity: Medium
Advisory: GHSA-6hrm-jqp3-64cv
CVE: CVE-2020-24393
CWE: CWE-295
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-6hrm-jqp3-64cv
Type: github-advisory

## Affected
- RubyGems: `tweetstream` — affected >=0

## Details
TweetStream 2.6.1 uses the library eventmachine in an insecure way that does not have TLS hostname validation. This allows an attacker to perform a man-in-the-middle attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24393
- https://github.com/tweetstream/tweetstream
- https://securitylab.github.com/advisories/GHSL-2020-096-tweetstream-tweetstream
