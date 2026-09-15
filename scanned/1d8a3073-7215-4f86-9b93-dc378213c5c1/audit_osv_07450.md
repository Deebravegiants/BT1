# [M] BIT-ruby-2020-10933

## Summary
Severity: Medium
Advisory: BIT-ruby-2020-10933
Aliases: BIT-ruby-min-2020-10933, CVE-2020-10933
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-ruby-2020-10933
Type: osv

## Affected
- Bitnami: `ruby` — affected >=2.7.0 <2.7.1

## Details
An issue was discovered in Ruby 2.5.x through 2.5.7, 2.6.x through 2.6.5, and 2.7.0. If a victim calls BasicSocket#read_nonblock(requested_size, buffer, exception: false), the method resizes the buffer to fit the requested size, but no data is copied. Thus, the buffer string provides the previous value of the heap. This may expose possibly sensitive data from the interpreter.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/F4TNVTT66VPRMX5UZYSDGSVRXKKDDDU5/
- https://security.netapp.com/advisory/ntap-20200625-0001/
- https://www.debian.org/security/2020/dsa-4721
- https://www.ruby-lang.org/en/news/2020/03/31/heap-exposure-in-socket-cve-2020-10933/
- https://nvd.nist.gov/vuln/detail/CVE-2020-10933
