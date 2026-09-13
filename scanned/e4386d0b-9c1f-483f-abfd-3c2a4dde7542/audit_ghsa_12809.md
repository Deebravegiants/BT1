# [C] Integer overflow in publify_core

## Summary
Severity: Critical
Advisory: GHSA-rc42-jghf-vr8f
CVE: CVE-2022-1812
CWE: CWE-190
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-14
Source: https://github.com/advisories/GHSA-rc42-jghf-vr8f
Type: github-advisory

## Affected
- RubyGems: `publify_core` — affected >=0 <9.2.10

## Details
Integer Overflow or Wraparound in GitHub repository publify/publify prior to 9.2.10 due to an unlimited length user name field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1812
- https://github.com/publify/publify/commit/29a5837c29620e33857d7a5afce01384e3f8e41a
- https://github.com/publify/publify_core
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/publify_core/CVE-2022-1812.yml
- https://huntr.dev/bounties/17d86a50-265c-4ec8-9592-0bd909ddc8f3
