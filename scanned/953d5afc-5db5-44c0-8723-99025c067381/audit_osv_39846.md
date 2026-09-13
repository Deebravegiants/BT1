# [M] Unbounded memory allocation in RFC6587SyslogDeserializer (octet-counted framing) — remote DoS

## Summary
Severity: Medium
Advisory: CVE-2026-47859
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-47859
Type: osv

## Details
RFC6587SyslogDeserializer, used by the Spring Integration syslog TCP inbound adapter to decode RFC 6587 / RFC 5424 frames, trusts the sender-supplied octet count of an octet-counted frame and allocates a byte array of exactly that size with no upper bound.
Spring Integration 7.1.0
Spring Integration 7.0.0 - 7.0.5
Spring Integration 6.5.0 - 6.5.10
Spring Integration 6.4.0 - 6.4.12
Spring Integration 5.5.21 and earlier

## References
- https://spring.io/security/cve-2026-47859
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47859.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47859
