# [H] Cookie exposure in requestretry

## Summary
Severity: High
Advisory: GHSA-hjp8-2cm3-cc45
CVE: CVE-2022-0654
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-24
Source: https://github.com/advisories/GHSA-hjp8-2cm3-cc45
Type: github-advisory

## Affected
- npm: `requestretry` — affected >=0 <7.0.0

## Details
Exposure of Sensitive Information to an Unauthorized Actor in GitHub repository fgribreau/node-request-retry prior to 7.0.0 via cookies being leaked to external sites.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0654
- https://github.com/fgribreau/node-request-retry/commit/0979c6001d9d57c2aac3157c11b007397158922a
- https://huntr.dev/bounties/a779faf5-c2cc-48be-a31d-4ddfac357afc
