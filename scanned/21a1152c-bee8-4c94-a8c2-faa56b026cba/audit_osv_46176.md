# [M] In affected libpcap versions during the setup of a remote packet capture the internal function...

## Summary
Severity: Medium
Advisory: JLSEC-2026-764
Ecosystem: Julia
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/JLSEC-2026-764
Type: osv

## Affected
- Julia: `libpcap_jll` — affected >=0 <1.10.5+0

## Details
In affected libpcap versions during the setup of a remote packet capture the internal function `sock_initaddress()` calls getaddrinfo() and possibly freeaddrinfo(), but does not clearly indicate to the caller function whether freeaddrinfo() still remains to be called after the function returns.  This makes it possible in some scenarios that both the function and its caller call freeaddrinfo() for the same allocated memory block.  A similar problem was reported in Apple libpcap, to which Apple assigned CVE-2023-40400.

## References
- https://github.com/advisories/GHSA-7m22-9mw3-j4pp
- https://github.com/the-tcpdump-group/libpcap/commit/262e4f34979872d822ccedf9f318ed89c4d31c03
- https://github.com/the-tcpdump-group/libpcap/commit/2aa69b04d8173b18a0e3492e0c8f2f7fabdf642d
- https://nvd.nist.gov/vuln/detail/CVE-2023-7256
