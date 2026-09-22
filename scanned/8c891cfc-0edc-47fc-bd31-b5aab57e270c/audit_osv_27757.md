# [H] Transfer requests received over DoH can lead to a denial of service in DNSdist

## Summary
Severity: High
Advisory: CVE-2024-25581
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-13
Source: https://osv.dev/vulnerability/CVE-2024-25581
Type: osv

## Details
When incoming DNS over HTTPS support is enabled using the nghttp2 provider, and queries are routed to a tcp-only or DNS over TLS backend, an attacker can trigger an assertion failure in DNSdist by sending a request for a zone transfer (AXFR or IXFR) over DNS over HTTPS, causing the process to stop and thus leading to a Denial of Service. DNS over HTTPS is not enabled by default, and backends are using plain DNS (Do53) by default.

## References
- http://www.openwall.com/lists/oss-security/2024/05/13/1
- https://repo.powerdns.com/
- https://dnsdist.org/security-advisories/powerdns-advisory-for-dnsdist-2024-03.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25581.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25581
- https://github.com/PowerDNS/pdns
