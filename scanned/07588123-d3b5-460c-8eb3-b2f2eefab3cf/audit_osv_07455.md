# [H] BIT-ruby-2026-46727

## Summary
Severity: High
Advisory: BIT-ruby-2026-46727
Aliases: BIT-ruby-min-2026-46727, CVE-2026-46727
Ecosystem: Bitnami
Published: 2026-05-27
Source: https://osv.dev/vulnerability/BIT-ruby-2026-46727
Type: osv

## Affected
- Bitnami: `ruby` — affected >=4.0.0 <4.0.5

## Details
An issue was discovered in Ruby 4 before 4.0.5. A race condition leading to a use-after-free in the pthread-based getaddrinfo timeout handler (rb_getaddrinfo in ext/socket/raddrinfo.c) allows a remote attacker who can delay DNS responses near the user-specified timeout to crash a Ruby process that calls Addrinfo.getaddrinfo(..., timeout:) or Socket.tcp(..., resolv_timeout:). Memory-corruption-based exploitation is theoretically possible. The attack could, for example, be carried out through a crafted authoritative DNS server or recursive resolver.

## References
- https://hackerone.com/reports/3607434
- https://nvd.nist.gov/vuln/detail/CVE-2026-46727
- https://www.ruby-lang.org/en/news/2026/05/20/getaddrinfo-cve-2026-46727/
