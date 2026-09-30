# [H] samlr XML nodes comment attack

## Summary
Severity: High
Advisory: GHSA-qpxp-5j56-gg3x
CVE: CVE-2018-20857
CWE: CWE-20
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-07-31
Source: https://github.com/advisories/GHSA-qpxp-5j56-gg3x
Type: github-advisory

## Affected
- RubyGems: `samlr` — affected >=0 <2.6.2

## Details
Zendesk Samlr before 2.6.2 allows an XML nodes comment attack such as a name_id node with user@example.com followed by `<!---->`. and then the attacker's domain name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20857
- https://github.com/zendesk/samlr/pull/29
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/samlr/CVE-2018-20857.yml
- https://github.com/zendesk/samlr
- https://github.com/zendesk/samlr/compare/v2.6.1...v2.6.2
