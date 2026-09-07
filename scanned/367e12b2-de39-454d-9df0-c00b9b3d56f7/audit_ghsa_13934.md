# [H] XML External Entity Reference in Apache NiFi

## Summary
Severity: High
Advisory: GHSA-hxjp-q6c3-38fx
CVE: CVE-2023-22832
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-02-10
Source: https://github.com/advisories/GHSA-hxjp-q6c3-38fx
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi-ccda-processors` — affected >=1.2.0 <1.20.0

## Details
The ExtractCCDAAttributes Processor in Apache NiFi 1.2.0 through 1.19.1 does not restrict XML External Entity references. Flow configurations that include the ExtractCCDAAttributes Processor are vulnerable to malicious XML documents that contain Document Type Declarations with XML External Entity references. The resolution disables Document Type Declarations and disallows XML External Entity resolution in the ExtractCCDAAttributes Processor.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-22832
- https://github.com/apache/nifi/commit/e966336e8966cf0cbbd12a2c4f2d73a7ceb75cd8
- https://github.com/apache/nifi
- https://lists.apache.org/thread/b51qs6y7b7r58vovddkv6wc16g2xbl3w
- https://nifi.apache.org/security.html#CVE-2023-22832
