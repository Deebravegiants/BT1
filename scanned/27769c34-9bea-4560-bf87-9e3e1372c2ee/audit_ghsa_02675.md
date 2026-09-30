# [H] Improper Restriction of XML External Entity Reference (XXE) in Nokogiri on JRuby

## Summary
Severity: High
Advisory: GHSA-2rr5-8q37-2w7h
CVE: CVE-2021-41098
CWE: CWE-611
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-09-27
Source: https://github.com/advisories/GHSA-2rr5-8q37-2w7h
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.12.5

## Details
### Severity

The Nokogiri maintainers have evaluated this as [**High Severity** 7.5 (CVSS3.0)](https://www.first.org/cvss/calculator/3.0#CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N/E:H/RL:O/RC:C/MAV:N/MAC:L) for JRuby users. (This security advisory does not apply to CRuby users.)


### Impact

In Nokogiri v1.12.4 and earlier, **on JRuby only**, the SAX parser resolves external entities by default.

Users of Nokogiri on JRuby who parse untrusted documents using any of these classes are affected:

- Nokogiri::XML::SAX::Parser
- Nokogiri::HTML4::SAX::Parser or its alias Nokogiri::HTML::SAX::Parser
- Nokogiri::XML::SAX::PushParser
- Nokogiri::HTML4::SAX::PushParser or its alias Nokogiri::HTML::SAX::PushParser


### Mitigation

JRuby users should upgrade to Nokogiri v1.12.5 or later. There are no workarounds available for v1.12.4 or earlier.

CRuby users are not affected.

## References
- https://github.com/sparklemotion/nokogiri/security/advisories/GHSA-2rr5-8q37-2w7h
- https://nvd.nist.gov/vuln/detail/CVE-2021-41098
- https://github.com/sparklemotion/nokogiri/commit/5bf729ff3cc84709ee3c3248c981584088bf9f6d
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nokogiri/CVE-2021-41098.yml
- https://github.com/sparklemotion/nokogiri
