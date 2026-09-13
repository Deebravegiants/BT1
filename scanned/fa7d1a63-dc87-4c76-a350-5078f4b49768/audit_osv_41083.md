# [M] Nokogiri: Possible Use-After-Free in XInclude Processing

## Summary
Severity: Medium
Advisory: CVE-2026-57438
Aliases: GHSA-wfpw-mmfh-qq69
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:N/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-57438
Type: osv

## Details
Nokogiri is an open source XML and HTML library for the Ruby programming language. Prior to 1.19.4, XInclude substitution performed by Nokogiri::XML::Node#do_xinclude replaced each <xi:include> in place, freeing the include node along with its children (such as <xi:fallback> and its descendants) and any namespaces declared on them. If an application had already exposed one of those nodes or namespaces to Ruby, the corresponding Ruby object was left pointing at freed memory. Using the object could result in invalid reads or writes to memory. This vulnerability is fixed in 1.19.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57438.json
- https://github.com/sparklemotion/nokogiri/security/advisories/GHSA-wfpw-mmfh-qq69
- https://nvd.nist.gov/vuln/detail/CVE-2026-57438
