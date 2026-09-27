# [M] Publify has Improper Access Controls

## Summary
Severity: Medium
Advisory: GHSA-c273-c6vg-4pv5
CVE: CVE-2022-1810
CWE: CWE-284, CWE-639, CWE-732
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c273-c6vg-4pv5
Type: github-advisory

## Affected
- RubyGems: `publify_core` — affected >=0 <9.2.9

## Details
A low-privileged user can modify and delete admin articles by changing the value of the `article[id]` parameter prior to 9.2.9.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1810
- https://github.com/publify/publify/commit/c0aba87844d1e47da50c0d99a3465164a4d244ce
- https://github.com/publify/publify
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/publify_core/CVE-2022-1810.yml
- https://huntr.dev/bounties/9b2d7579-032e-42da-b736-4b10a868eacb
