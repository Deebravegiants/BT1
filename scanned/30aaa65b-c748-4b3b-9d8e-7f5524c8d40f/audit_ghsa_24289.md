# [H] Multiple components in Apache NiFi do not restrict XML External Entity references

## Summary
Severity: High
Advisory: GHSA-wc97-7623-rxwx
CVE: CVE-2022-29265
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-wc97-7623-rxwx
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi` — affected >=0.0.1 <1.16.1

## Details
Apache NiFi is a system to process and distribute data. Multiple components in Apache NiFi 0.0.1 to 1.16.0 do not restrict XML External Entity references in the default configuration. The Standard Content Viewer service attempts to resolve XML External Entity references when viewing formatted XML files. The following Processors attempt to resolve XML External Entity references when configured with default property values: 
- EvaluateXPath 
- EvaluateXQuery 
- ValidateXml 

Apache NiFi flow configurations that include these Processors are vulnerable to malicious XML documents that contain Document Type Declarations with XML External Entity references. NiFi 1.16.1 disables Document Type Declarations in the default configuration for these Processors and disallows XML External Entity resolution in standard services.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29265
- https://github.com/apache/nifi
- https://lists.apache.org/thread/47od9kr9n4cyv0mv81jh3pkyx815kyjl
- https://nifi.apache.org/security.html#CVE-2022-29265
