# [H] Apache Struts: File leak in multipart request processing causes disk exhaustion (DoS)

## Summary
Severity: High
Advisory: CVE-2025-64775
Aliases: GHSA-xx7v-hqxh-cjr9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-01
Source: https://osv.dev/vulnerability/CVE-2025-64775
Type: osv

## Details
Denial of Service vulnerability in Apache Struts, file leak in multipart request processing causes disk exhaustion.

This issue affects Apache Struts: from 2.0.0 through 6.7.0, from 7.0.0 through 7.0.3.

Users are recommended to upgrade to version 6.8.0 or 7.1.1, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/12/01/2
- https://repo.maven.apache.org/maven2
- https://cwiki.apache.org/confluence/display/WW/S2-068
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64775.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-64775
