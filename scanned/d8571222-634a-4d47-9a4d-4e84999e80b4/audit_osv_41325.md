# [M] EmbeddedHeadersJsonMessageMapper default gives wire peer full control of MessageHeaders

## Summary
Severity: Medium
Advisory: CVE-2026-59322
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-59322
Type: osv

## Details
The EmbeddedHeadersJsonMessageMapper defaults to an overly permissive header parsing posture in its constructor. When decodeNativeFormat processes raw byte payloads, it deserializes embedded JSON headers into a plain Map and constructs a GenericMessage with MutableMessageHeaders without sanitizing or filtering untrusted header names by default.
Spring Integration 7.1.0
Spring Integration 7.0.0 - 7.0.5
Spring Integration 6.5.0 - 6.5.10
Spring Integration 6.4.0 - 6.4.12
Spring Integration 5.5.21 and earlier

## References
- https://spring.io/security/cve-2026-59322
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59322.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59322
