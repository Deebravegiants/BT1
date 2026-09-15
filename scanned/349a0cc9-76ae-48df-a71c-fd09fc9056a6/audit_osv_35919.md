# [C] dns: memory‑safety issue in the DNS name parser

## Summary
Severity: Critical
Advisory: CVE-2026-1678
Aliases: GHSA-536f-h63g-hj42
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-1678
Type: osv

## Details
dns_unpack_name() caches the buffer tailroom once and reuses it while appending DNS labels. As the buffer grows, the cached size becomes incorrect, and the final null terminator can be written past the buffer. With assertions disabled (default), a malicious DNS response can trigger an out-of-bounds write when CONFIG_DNS_RESOLVER is enabled.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/1xxx/CVE-2026-1678.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-536f-h63g-hj42
- https://nvd.nist.gov/vuln/detail/CVE-2026-1678
- https://github.com/zephyrproject-rtos/zephyr
