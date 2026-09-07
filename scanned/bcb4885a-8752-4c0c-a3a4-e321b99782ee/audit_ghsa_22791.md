# [M] Cross-site Scripting in Apache Sling XSS Protection API

## Summary
Severity: Medium
Advisory: GHSA-7mfw-43c4-45mq
CVE: CVE-2017-15717
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-7mfw-43c4-45mq
Type: github-advisory

## Affected
- Maven: `org.apache.sling:org.apache.sling.xss` — affected >=1.0.4 <2.0.4
- Maven: `org.apache.sling:org.apache.sling.xss.compat` — affected 1.1.0

## Details
A flaw in the way URLs are escaped and encoded in the org.apache.sling.xss.impl.XSSAPIImpl#getValidHref and org.apache.sling.xss.impl.XSSFilterImpl#isValidHref allows special crafted URLs to pass as valid, although they carry XSS payloads. The affected versions are Apache Sling XSS Protection API 1.0.4 to 1.0.18, Apache Sling XSS Protection API Compat 1.1.0 and Apache Sling XSS Protection API 2.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15717
- https://s.apache.org/CVE-2017-15717
