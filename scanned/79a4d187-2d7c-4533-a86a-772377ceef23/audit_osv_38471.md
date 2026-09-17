# [M] Denial of service via crafted DoH3 queries

## Summary
Severity: Medium
Advisory: CVE-2026-40211
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-40211
Type: osv

## Details
An attacker can send crafted DNS over HTTP/3 queries, triggering an exception that prevents some buffer from being freed right away. The buffer will be freed at the end of the QUIC connection, but on some setups it might be possible to open enough concurrent DoH3 streams to trigger an out-of-memory condition, resulting in a denial of service.

## References
- https://repo.powerdns.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40211.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40211
- https://www.dnsdist.org/security-advisories/powerdns-advisory-for-dnsdist-2026-09.html
- https://github.com/PowerDNS/pdns
