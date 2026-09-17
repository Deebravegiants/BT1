# [M] openssl_encrypt before 1.4.9 D-Bus Properties Authorization Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-81686
Aliases: GHSA-7fhx-8rmv-qjj3, PYSEC-2026-3794
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81686
Type: osv

## Details
openssl_encrypt 1.4.x before 1.4.9 contains an optional D-Bus crypto service whose org.freedesktop.DBus.Properties.Set method performs neither a polkit authorization check nor value validation. Any local user on the system bus can call Set without authorization and set MaxConcurrentOperations (to 0/negative, causing the concurrency gate to refuse all subsequent operations, or to a huge value removing the limit) or the unbounded DefaultTimeout, resulting in a persistent denial of service of the root daemon. The D-Bus service exists only on the 1.4.x line and was removed in 1.5.x.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81686.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-7fhx-8rmv-qjj3
- https://nvd.nist.gov/vuln/detail/CVE-2026-81686
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-d-bus-properties-authorization-bypass
