# [C] libxmljs vulnerable to type confusion when parsing specially crafted XML 

## Summary
Severity: Critical
Advisory: GHSA-mg49-jqgw-gcj6
CVE: CVE-2024-34392
CWE: CWE-843
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-02
Source: https://github.com/advisories/GHSA-mg49-jqgw-gcj6
Type: github-advisory

## Affected
- npm: `libxmljs` — affected >=0

## Details
libxmljs is vulnerable to a type confusion vulnerability when parsing a specially crafted XML while invoking the `namespaces()` function (which invokes `_wrap__xmlNode_nsDef_get()`) on a grand-child of a node that refers to an entity. This vulnerability can lead to denial of service and remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34392
- https://github.com/libxmljs/libxmljs/issues/646
- https://github.com/libxmljs/libxmljs
- https://research.jfrog.com/vulnerabilities/libxmljs-namespaces-type-confusion-rce-jfsa-2024-001034096
