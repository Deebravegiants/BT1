# [M] Apache CXF allows unrestricted memory consumption in CXF HTTP clients

## Summary
Severity: Medium
Advisory: GHSA-4mgg-fqfq-64hg
CVE: CVE-2024-41172
CWE: CWE-401
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-07-19
Source: https://github.com/advisories/GHSA-4mgg-fqfq-64hg
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-rt-transports-http` — affected >=4.0.0 <4.0.5
- Maven: `org.apache.cxf:cxf-rt-transports-http` — affected >=3.6.0 <3.6.4

## Details
In versions of Apache CXF before 3.6.4 and 4.0.5 (3.5.x and lower versions are not impacted), a CXF HTTP client conduit may prevent HTTPClient instances from being garbage collected and it is possible that memory consumption will continue to increase, eventually causing the application to run  out of memory

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41172
- https://github.com/apache/cxf
- https://lists.apache.org/thread/n2hvbrgwpdtcqdccod8by28ynnolybl6
