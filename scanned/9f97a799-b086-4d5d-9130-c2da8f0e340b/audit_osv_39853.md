# [M] DefaultJmsHeaderMapper copies all JMS user properties into MessageHeaders without excluding framework-significant names

## Summary
Severity: Medium
Advisory: CVE-2026-47880
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-47880
Type: osv

## Details
A producer who can publish to a JMS destination consumed by any Spring Integration JMS inbound component can set String JMS properties named replyChannel, errorChannel, or json__TypeId__ which are copied verbatim into the Spring Integration MessageHeaders.
Spring Integration 7.1.0
Spring Integration 7.0.0 - 7.0.5
Spring Integration 6.5.0 - 6.5.10
Spring Integration 6.4.0 - 6.4.12
Spring Integration 5.5.21 and earlier

## References
- https://spring.io/security/cve-2026-47880
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47880.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47880
