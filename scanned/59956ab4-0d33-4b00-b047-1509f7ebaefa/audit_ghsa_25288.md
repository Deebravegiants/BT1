# [M] Publify exposes article metadata

## Summary
Severity: Medium
Advisory: GHSA-5jm7-g527-m694
CVE: CVE-2022-1553
CWE: CWE-863
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5jm7-g527-m694
Type: github-advisory

## Affected
- RubyGems: `publify_core` — affected >=0 <9.2.8

## Details
Leaking password protected articles content due to improper access control in GitHub repository publify/publify prior to 9.2.8. Attackers can leverage this vulnerability to view the contents of any password-protected article present on the publify website, compromising confidentiality and integrity of users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1553
- https://github.com/publify/publify/commit/1a78f16f460847274265a12a9555b3524892d7db
- https://github.com/publify/publify
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/publify_core/CVE-2022-1553.yml
- https://huntr.dev/bounties/b398e4c9-6cdf-4973-ad86-da796cde221f
