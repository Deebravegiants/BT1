# [H] Deserialization allow-list silently bypassed: setBeanClassLoader replaces deserializer but mapper keeps stale reference

## Summary
Severity: High
Advisory: CVE-2026-59307
CVSS: 8.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-59307
Type: osv

## Details
An operator who calls JdbcMessageStore.addAllowedPatterns(...) to restrict deserialization receives no protection at all when the store is a Spring-managed bean.
Spring Integration 7.1.0
Spring Integration 7.0.0 - 7.0.5
Spring Integration 6.5.0 - 6.5.10
Spring Integration 6.4.0 - 6.4.12

## References
- https://spring.io/security/cve-2026-59307
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59307.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59307
