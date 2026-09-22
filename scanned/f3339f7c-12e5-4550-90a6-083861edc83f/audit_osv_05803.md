# [H] Denial of service vulnerability in HAProxy mjson library

## Summary
Severity: High
Advisory: BIT-haproxy-2025-11230
Aliases: CVE-2025-11230
Ecosystem: Bitnami
Published: 2025-12-20
Source: https://osv.dev/vulnerability/BIT-haproxy-2025-11230
Type: osv

## Affected
- Bitnami: `haproxy` — affected >=3.2.0 <3.2.6

## Details
Inefficient algorithm complexity in mjson in HAProxy allows remote attackers to cause a denial of service via specially crafted JSON requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11230
- https://www.haproxy.com/blog/october-2025-cve-2025-11230-haproxy-mjson-library-denial-of-service-vulnerability
