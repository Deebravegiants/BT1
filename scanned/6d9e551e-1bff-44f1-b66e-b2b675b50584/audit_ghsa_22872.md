# [H] Nokogiri Improperly Handles Unexpected Data Type

## Summary
Severity: High
Advisory: GHSA-xh29-r2w5-wx8m
CVE: CVE-2022-29181
CWE: CWE-241, CWE-843
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2022-05-23
Source: https://github.com/advisories/GHSA-xh29-r2w5-wx8m
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.13.6

## Details
### Summary

Nokogiri `< v1.13.6` does not type-check all inputs into the XML and HTML4 SAX parsers. For CRuby users, this may allow specially crafted untrusted inputs to cause illegal memory access errors (segfault) or reads from unrelated memory.

### Severity

The Nokogiri maintainers have evaluated this as **High 8.2** (CVSS3.1).


### Mitigation

CRuby users should upgrade to Nokogiri `>= 1.13.6`.

JRuby users are not affected.


### Workarounds

To avoid this vulnerability in affected applications, ensure the untrusted input is a `String` by calling `#to_s` or equivalent.


### Credit

This vulnerability was responsibly reported by @agustingianni and the Github Security Lab.

## References
- https://github.com/sparklemotion/nokogiri/security/advisories/GHSA-xh29-r2w5-wx8m
- https://nvd.nist.gov/vuln/detail/CVE-2022-29181
- https://github.com/sparklemotion/nokogiri/commit/83cc451c3f29df397caa890afc3b714eae6ab8f7
- https://github.com/sparklemotion/nokogiri/commit/db05ba9a1bd4b90aa6c76742cf6102a7c7297267
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nokogiri/CVE-2022-29181.yml
- https://github.com/sparklemotion/nokogiri
- https://github.com/sparklemotion/nokogiri/releases/tag/v1.13.6
- https://security.gentoo.org/glsa/202208-29
- https://securitylab.github.com/advisories/GHSL-2022-031_GHSL-2022-032_Nokogiri
- https://support.apple.com/kb/HT213532
- http://seclists.org/fulldisclosure/2022/Dec/23
