# [H] Apache CXF: SSRF vulnerability via WADL stylesheet parameter

## Summary
Severity: High
Advisory: GHSA-5m3j-pxh7-455p
CVE: CVE-2024-29736
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-19
Source: https://github.com/advisories/GHSA-5m3j-pxh7-455p
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-rt-rs-service-description` — affected >=4.0.0 <4.0.5
- Maven: `org.apache.cxf:cxf-rt-rs-service-description` — affected >=3.6.0 <3.6.4
- Maven: `org.apache.cxf:cxf-rt-rs-service-description` — affected >=0 <3.5.9

## Details
A SSRF vulnerability in WADL service description in versions of Apache CXF before 4.0.5, 3.6.4 and 3.5.9 allows an attacker to perform SSRF style attacks on REST webservices. The attack only applies if a custom stylesheet parameter is configured.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29736
- https://github.com/apache/cxf/commit/378afe1acb7503315bc63555c8743db0f55d8312
- https://github.com/apache/cxf/commit/bafb0cadf723fc3962031c34f1f20dc0e8b7a36b
- https://github.com/apache/cxf/commit/df2241c59481a57aebb1c0693b778a35baaf5570
- https://github.com/apache/cxf
- https://lists.apache.org/thread/4jtpsswn2r6xommol54p5mg263ysgdw2
