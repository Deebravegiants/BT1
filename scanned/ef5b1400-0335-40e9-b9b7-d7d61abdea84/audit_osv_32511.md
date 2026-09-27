# [H] TEIGarage XML External Entity (XXE) Injection in Document Conversion Service

## Summary
Severity: High
Advisory: CVE-2025-31497
Aliases: GHSA-w2hq-3cjc-2x55
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-31497
Type: osv

## Details
TEIGarage is a webservice and RESTful service to transform, convert and validate various formats, focussing on the TEI format. The Document Conversion Service contains a critical XML External Entity (XXE) Injection vulnerability in its document conversion functionality. The service processes XML files during the conversion process but fails to disable external entity processing, allowing an attacker to read arbitrary files from the server's filesystem. This vulnerability could allow attackers to read sensitive files from the server's filesystem, potentially exposing configuration files, credentials, or other confidential information. Additionally, depending on the server configuration, this could potentially be used to perform server-side request forgery (SSRF) attacks by making the server connect to internal services. This issue is patched in version 1.2.4. A workaround for this vulnerability includes disabling external entity processing in the XML parser by setting the appropriate security features (e.g., XMLConstants.FEATURE_SECURE_PROCESSING).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/31xxx/CVE-2025-31497.json
- https://github.com/TEIC/TEIGarage/security/advisories/GHSA-w2hq-3cjc-2x55
- https://nvd.nist.gov/vuln/detail/CVE-2025-31497
