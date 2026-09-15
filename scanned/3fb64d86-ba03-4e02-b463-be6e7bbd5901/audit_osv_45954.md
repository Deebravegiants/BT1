# [H] JLSEC-2026-515

## Summary
Severity: High
Advisory: JLSEC-2026-515
Ecosystem: Julia
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/JLSEC-2026-515
Type: osv

## Affected
- Julia: `ZeroMQ_jll` — affected >=0 <4.3.4+0

## Details
There's a flaw in the zeromq server in versions before 4.3.3 in `src/decoder_allocators.hpp`. The decoder static allocator could have its sized changed, but the buffer would remain the same as it is a static buffer. A remote, unauthenticated attacker who sends a crafted request to the zeromq server could trigger a buffer overflow WRITE of arbitrary data if CURVE/ZAP authentication is not enabled. The greatest impact of this flaw is to application availability, data integrity, and confidentiality.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1921983
- https://github.com/zeromq/libzmq/security/advisories/GHSA-fc3w-qxf5-7hp6
