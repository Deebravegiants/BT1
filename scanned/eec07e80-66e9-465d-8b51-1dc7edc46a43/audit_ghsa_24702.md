# [M] Publify Incorrect Authorization

## Summary
Severity: Medium
Advisory: GHSA-79m3-q3wh-c3qm
CVE: CVE-2022-0574
CWE: CWE-863
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-79m3-q3wh-c3qm
Type: github-advisory

## Affected
- RubyGems: `publify_core` — affected >=0 <9.2.8

## Details
Improper Access Control in GitHub repository publify/publify prior to 9.2.8. Anonymous users can't view but can leave comments on an article in draft mode.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0574
- https://github.com/publify/publify/commit/0e6c66ac2002136517662399bca9d838c80d9739
- https://github.com/publify/publify
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/publify_core/CVE-2022-0574.yml
- https://huntr.dev/bounties/6f322c84-9e20-4df6-97e8-92bc271ede3f
