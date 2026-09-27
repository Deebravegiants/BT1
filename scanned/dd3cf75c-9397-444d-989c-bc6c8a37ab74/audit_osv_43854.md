# [M] jsoup Uncontrolled Resource Consumption in XmlTreeBuilder

## Summary
Severity: Medium
Advisory: CVE-2026-75140
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-75140
Type: osv

## Details
jsoup through 1.23.2, fixed in commit 862ba2f, contains an uncontrolled resource consumption vulnerability in XmlTreeBuilder that allows remote attackers to exhaust JVM heap memory by supplying a deeply nested XML document with uniquely-namespaced elements. The builder copies the entire inherited namespace map on every start element, causing quadratic time and memory complexity, which attackers can exploit to trigger an OutOfMemoryError and terminate the application.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75140.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75140
- https://www.vulncheck.com/advisories/jsoup-uncontrolled-resource-consumption-in-xmltreebuilder
- https://github.com/jhy/jsoup/pull/2556
- https://github.com/jhy/jsoup/commit/862ba2f1d48ee95609183dbcfc848c9fd7afc76a
- https://github.com/jhy/jsoup
