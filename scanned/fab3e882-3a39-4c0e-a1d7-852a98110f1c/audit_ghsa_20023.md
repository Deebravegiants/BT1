# [H] Unchecked return value from xmlTextReaderExpand

## Summary
Severity: High
Advisory: GHSA-qv4q-mr5r-qprj
CVE: CVE-2022-23476
CWE: CWE-252, CWE-476
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-08
Source: https://github.com/advisories/GHSA-qv4q-mr5r-qprj
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=1.13.8 <1.13.10

## Details
## Summary

Nokogiri `1.13.8, 1.13.9` fails to check the return value from `xmlTextReaderExpand` in the method `Nokogiri::XML::Reader#attribute_hash`. This can lead to a null pointer exception when invalid markup is being parsed. 

For applications using `XML::Reader` to parse untrusted inputs, this may potentially be a vector for a denial of service attack.


## Mitigation

Upgrade to Nokogiri `>= 1.13.10`.

Users may be able to search their code for calls to either `XML::Reader#attributes` or `XML::Reader#attribute_hash` to determine if they are affected.


## Severity

The Nokogiri maintainers have evaluated this as [High Severity 7.5 (CVSS3.1)](https://www.first.org/cvss/calculator/3.1#CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H).


## References

- [CWE - CWE-252: Unchecked Return Value (4.9)](https://cwe.mitre.org/data/definitions/252.html)
- [CWE - CWE-476: NULL Pointer Dereference (4.9)](https://cwe.mitre.org/data/definitions/476.html)


## Credit

This vulnerability was responsibly reported by @davidwilemski.

## References
- https://github.com/sparklemotion/nokogiri/security/advisories/GHSA-qv4q-mr5r-qprj
- https://nvd.nist.gov/vuln/detail/CVE-2022-23476
- https://github.com/sparklemotion/nokogiri/commit/85410e38410f670cbbc8c5b00d07b843caee88ce
- https://github.com/sparklemotion/nokogiri/commit/9fe0761c47c0d4270d1a5220cfd25de080350d50
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nokogiri/CVE-2022-23476.yml
- https://github.com/sparklemotion/nokogiri
