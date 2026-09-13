# [M] CVE-2021-43797

## Summary
Severity: Medium
Advisory: CVE-2021-43797
Aliases: GHSA-wx5j-54mm-rqqq
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2021-12-09
Source: https://osv.dev/vulnerability/CVE-2021-43797
Type: osv

## Details
Netty is an asynchronous event-driven network application framework for rapid development of maintainable high performance protocol servers & clients. Netty prior to version 4.1.71.Final skips control chars when they are present at the beginning / end of the header name. It should instead fail fast as these are not allowed by the spec and could lead to HTTP request smuggling. Failing to do the validation might cause netty to "sanitize" header names before it forward these to another remote system when used as proxy. This remote system can't see the invalid usage anymore, and therefore does not do the validation itself. Users should upgrade to version 4.1.71.Final.

## References
- https://github.com/netty/netty/security/advisories/GHSA-wx5j-54mm-rqqq
- https://lists.debian.org/debian-lts-announce/2023/01/msg00008.html
- https://security.netapp.com/advisory/ntap-20220107-0003/
- https://www.debian.org/security/2023/dsa-5316
- https://github.com/netty/netty/commit/07aa6b5938a8b6ed7a6586e066400e2643897323
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
