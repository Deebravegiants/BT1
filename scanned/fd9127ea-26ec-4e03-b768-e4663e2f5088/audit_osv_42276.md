# [H] Apache Neethi: Uncontrolled recursion in policy processing

## Summary
Severity: High
Advisory: CVE-2026-66142
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-66142
Type: osv

## Details
Apache Neethi is vulnerable to uncontrolled recursion when parsing policies that lack policy Ids or with deeply nested structures, which may lead to a denial of service attack when parsing policies due to runtime memory exhaustion. Users are recommended to upgrade to version 3.2.3, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/24/8
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66142.json
- https://lists.apache.org/thread/fomwtwt4pzzhxn4fyn3skykto913vfzt
- https://nvd.nist.gov/vuln/detail/CVE-2026-66142
