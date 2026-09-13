# [M] net:  TLS 1.2 connections allowed  on TLS 1.3 sockets

## Summary
Severity: Medium
Advisory: CVE-2026-1677
Aliases: GHSA-23r2-m5wx-4rvq
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-1677
Type: osv

## Details
Zephyr sockets created with `IPPROTO_TLS_1_3` can still negotiate a TLS 1.2 connection when both TLS versions are enabled in Kconfig, because the socket-level protocol selection is not propagated to mbedTLS (e.g. via `mbedtls_ssl_conf_min_tls_version`). The ClientHello advertises both versions and the peer can establish TLS 1.2, so applications that assumed `IPPROTO_TLS_1_3` enforces TLS 1.3 may silently use TLS 1.2 and remain exposed to TLS 1.2-specific weaknesses. As a workaround, the `TLS_CIPHERSUITE_LIST` socket option can be restricted to TLS 1.3-only cipher suites.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/1xxx/CVE-2026-1677.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-23r2-m5wx-4rvq
- https://nvd.nist.gov/vuln/detail/CVE-2026-1677
- https://github.com/zephyrproject-rtos/zephyr
