# [H] Nokogiri implementation of libxslt vulnerable to heap corruption

## Summary
Severity: High
Advisory: GHSA-vmfx-gcfq-wvm2
CVE: CVE-2019-5815
CWE: CWE-787, CWE-843
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vmfx-gcfq-wvm2
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.10.5

## Details
Type confusion in `xsltNumberFormatGetMultipleLevel` prior to libxslt 1.1.33 could allow attackers to potentially exploit heap corruption via crafted XML data.

Nokogiri prior to version 1.10.5 contains a vulnerable version of libxslt. Nokogiri version 1.10.5 upgrades the dependency to libxslt 1.1.34, which contains a patch for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5815
- https://github.com/sparklemotion/nokogiri/issues/2630
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nokogiri/CVE-2019-5815.yml
- https://github.com/sparklemotion/nokogiri
- https://gitlab.gnome.org/GNOME/libxslt/commit/08b62c25871b38d5d573515ca8a065b4b8f64f6b
- https://lists.debian.org/debian-lts-announce/2022/09/msg00010.html
