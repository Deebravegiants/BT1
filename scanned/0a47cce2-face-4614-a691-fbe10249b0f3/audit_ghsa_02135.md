# [M] Injection/XSS in Redcarpet

## Summary
Severity: Medium
Advisory: GHSA-q3wr-qw3g-3p4h
CVE: CVE-2020-26298
CWE: CWE-74, CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2021-01-11
Source: https://github.com/advisories/GHSA-q3wr-qw3g-3p4h
Type: github-advisory

## Affected
- RubyGems: `redcarpet` — affected >=0 <3.5.1

## Details
Redcarpet is a Ruby library for Markdown processing. In Redcarpet before version 3.5.1, there is an injection vulnerability which can enable a cross-site scripting attack. In affected versions no HTML escaping was being performed when processing quotes. This applies even when the `:escape_html` option was being used.  This is fixed in version 3.5.1 by the referenced commit.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26298
- https://github.com/vmg/redcarpet/commit/a699c82292b17c8e6a62e1914d5eccc252272793
- https://github.com/advisories/GHSA-q3wr-qw3g-3p4h
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/redcarpet/CVE-2020-26298.yml
- https://github.com/vmg/redcarpet
- https://github.com/vmg/redcarpet/blob/master/CHANGELOG.md#version-351-security
- https://lists.debian.org/debian-lts-announce/2021/01/msg00014.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BFMYDIONVWATY7EB6EARDVXT47AYCRNM
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FNO4ZZUPGAEUXKQL4G2HRIH7CUZKPCT6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PXNNWHHAPREDM3XJDACYRTK7DBMUONBI
- https://rubygems.org/gems/redcarpet
- https://www.debian.org/security/2021/dsa-4831
