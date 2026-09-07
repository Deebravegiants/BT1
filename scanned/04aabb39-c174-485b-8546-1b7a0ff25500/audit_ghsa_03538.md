# [M] Improper Certificate Validation in twitter-stream

## Summary
Severity: Medium
Advisory: GHSA-p6p8-q4pj-f74m
CVE: CVE-2020-24392
CWE: CWE-295
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-03-29
Source: https://github.com/advisories/GHSA-p6p8-q4pj-f74m
Type: github-advisory

## Affected
- RubyGems: `twitter-stream` — affected >=0

## Details
In voloko twitter-stream 0.1.16, missing TLS hostname validation allows an attacker to perform a man-in-the-middle attack against users of the library (because eventmachine is misused).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24392
- https://github.com/voloko/twitter-stream
- https://securitylab.github.com/advisories/GHSL-2020-097-voloko-twitter-stream
