# [M] BIT-ruby-2024-27282

## Summary
Severity: Medium
Advisory: BIT-ruby-2024-27282
Aliases: BIT-ruby-min-2024-27282, CVE-2024-27282
Ecosystem: Bitnami
Published: 2024-06-04
Source: https://osv.dev/vulnerability/BIT-ruby-2024-27282
Type: osv

## Affected
- Bitnami: `ruby` — affected >=3.3.0 <3.3.1

## Details
An issue was discovered in Ruby 3.x through 3.3.0. If attacker-supplied data is provided to the Ruby regex compiler, it is possible to extract arbitrary heap data relative to the start of the text, including pointers and sensitive strings. The fixed versions are 3.0.7, 3.1.5, 3.2.4, and 3.3.1.

## References
- https://hackerone.com/reports/2122624
- https://www.ruby-lang.org/en/news/2024/04/23/arbitrary-memory-address-read-regexp-cve-2024-27282/
- https://security.netapp.com/advisory/ntap-20241011-0007/
- https://nvd.nist.gov/vuln/detail/CVE-2024-27282
- https://lists.debian.org/debian-lts-announce/2024/09/msg00000.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/27LUWREIFTP3MQAW7QE4PJM4DPAQJWXF/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XYDHPHEZI7OQXTQKTDZHGZNPIJH7ZV5N/
