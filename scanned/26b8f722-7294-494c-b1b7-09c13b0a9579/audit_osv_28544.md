# [H] libxmljs attrs type confusion RCE

## Summary
Severity: High
Advisory: CVE-2024-34391
Aliases: GHSA-6433-x5p4-8jc7
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-02
Source: https://osv.dev/vulnerability/CVE-2024-34391
Type: osv

## Details
libxmljs is vulnerable to a type confusion vulnerability when parsing a specially crafted XML while invoking a function on the result of attrs() that was called on a parsed node. This vulnerability might lead to denial of service (on both 32-bit systems and 64-bit systems), data leak, infinite loop and remote code execution (on 32-bit systems with the XML_PARSE_HUGE flag enabled).

## References
- https://research.jfrog.com/vulnerabilities/libxmljs-attrs-type-confusion-rce-jfsa-2024-001033988/
- https://www.npmjs.com
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34391.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34391
- https://github.com/libxmljs/libxmljs/issues/645
