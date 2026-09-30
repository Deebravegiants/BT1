# [C] Spring Security embedded UnboundID LDAP server exposes well-known administrative bind DN on all network interfaces

## Summary
Severity: Critical
Advisory: CVE-2026-59270
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-59270
Type: osv

## Details
Spring Security's embedded UnboundID LDAP server (UnboundIdContainer) unconditionally registers an administrative credential and binds its listener to all available network interfaces.
Spring Security 7.1.0
Spring Security 7.0.0 - 7.0.6
Spring Security 6.5.0 - 6.5.11
Spring Security 6.4.0 - 6.4.18
Spring Security 5.8.0 - 5.8.27
Spring Security 5.7.0 - 5.7.25

## References
- https://spring.io/security/cve-2026-59270
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59270.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59270
