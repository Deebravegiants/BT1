# [M] Nokogiri before 1.18.4 Use-After-Free via libxslt

## Summary
Severity: Medium
Advisory: CVE-2025-71406
Aliases: GHSA-mrxw-mxhj-p664
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2025-71406
Type: osv

## Details
Nokogiri before 1.18.4 bundles a vulnerable version of libxslt (prior to 1.1.43) that contains two use-after-free vulnerabilities: CVE-2025-24855 (use-after-free of the XPath context node due to xsltEvalXPathStringNs leaking xpathCtxt->node) and CVE-2024-55549 (use-after-free related to excluded result prefixes/namespaces). Processing crafted XSLT can trigger memory corruption. Nokogiri 1.18.4 upgrades the bundled libxslt to 1.1.43 to resolve these issues.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71406.json
- https://github.com/sparklemotion/nokogiri/security/advisories/GHSA-mrxw-mxhj-p664
- https://nvd.nist.gov/vuln/detail/CVE-2025-71406
- https://www.vulncheck.com/advisories/nokogiri-before-use-after-free-via-libxslt
