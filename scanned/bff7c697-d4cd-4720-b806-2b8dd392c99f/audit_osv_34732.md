# [H] ZimaOS is vulnerable to Server-Side Request Forgery (SSRF)

## Summary
Severity: High
Advisory: CVE-2025-64427
Aliases: GHSA-m8hj-7xg5-p375
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:L)
Published: 2026-03-02
Source: https://osv.dev/vulnerability/CVE-2025-64427
Type: osv

## Details
ZimaOS is a fork of CasaOS, an operating system for Zima devices and x86-64 systems with UEFI. In version 1.5.0 and prior, due to insufficient validation or restriction of target URLs, an authenticated local user can craft requests that target internal IP addresses (e.g., 127.0.0.1, localhost, or private network ranges). This allows the attacker to interact with internal HTTP/HTTPS services that are not intended to be exposed externally or to local users. No known patch is publicly available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64427.json
- https://github.com/IceWhaleTech/ZimaOS/security/advisories/GHSA-m8hj-7xg5-p375
- https://nvd.nist.gov/vuln/detail/CVE-2025-64427
