# [H] Apache CXF: Untrusted JMS configuration can lead to RCE

## Summary
Severity: High
Advisory: GHSA-2hvc-5c6v-f533
CVE: CVE-2026-44417
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-2hvc-5c6v-f533
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-rt-transports-jms` — affected >=4.2.0 <4.2.1
- Maven: `org.apache.cxf:cxf-rt-transports-jms` — affected >=4.1.0 <4.1.6
- Maven: `org.apache.cxf:cxf-rt-transports-jms` — affected >=0 <3.6.11

## Details
The fix for CVE-2025-48913: `Apache CXF: Untrusted JMS configuration can lead to RCE` was not complete, meaning that another path in the code might lead to code execution capabilities, if untrusted users are allowed to configure JMS for Apache CXF. 
Users are recommended to upgrade to versions 4.2.1, 4.1.6 or 3.6.11, which fix this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-44417
- https://github.com/apache/cxf
- https://lists.apache.org/thread/bqg6gjy2cx7rfyqjxcpv3jwjvmclvz4o
