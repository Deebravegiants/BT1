# [H] Apache CXF: XXE via WSDL/XSD import parsing

## Summary
Severity: High
Advisory: CVE-2026-65432
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-65432
Type: osv

## Details
Apache CXF reads a top-level WSDL through its hardened StaxUtils path, which disables XML DTDs and external entities. However, any <wsdl:import> or <xsd:import> referenced from that top-level WSDL is handed off to WSDL4J, which does not disable DOCTYPE declarations or external entities. As a result, the protections applied to the top-level document do not extend to imported documents, leaving imported WSDL/XSD content vulnerable to XML External Entity (XXE) attacks. Users are recommended to upgrade to versions 4.2.3 or 4.1.8 or 3.6.12, which fix this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/06/17
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65432.json
- https://lists.apache.org/thread/5qs207krzg51jl3zs3cvnl5lt9njp8c3
- https://nvd.nist.gov/vuln/detail/CVE-2026-65432
