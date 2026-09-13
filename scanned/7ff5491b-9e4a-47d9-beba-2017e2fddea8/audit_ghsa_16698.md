# [C] libxmljs2 type confusion vulnerability when parsing specially crafted XML

## Summary
Severity: Critical
Advisory: GHSA-mjr4-7xg5-pfvh
CVE: CVE-2024-34393
CWE: CWE-843
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-02
Source: https://github.com/advisories/GHSA-mjr4-7xg5-pfvh
Type: github-advisory

## Affected
- npm: `libxmljs2` — affected >=0

## Details
libxmljs2 is vulnerable to type confusion when parsing a specially crafted XML while invoking a function on the result of attrs() that was called on a parsed node. This vulnerability might lead to denial of service (on both 32-bit systems and 64-bit systems), data leak, infinite loop and remote code execution (on 32-bit systems with the XML_PARSE_HUGE flag enabled). At the time of publication, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34393
- https://github.com/marudor/libxmljs2/issues/204
- https://github.com/marudor/libxmljs2
- https://research.jfrog.com/vulnerabilities/libxmljs2-attrs-type-confusion-rce-jfsa-2024-001034097
