# [H] net: fix __dst_negative_advice() race

## Summary
Severity: High
Advisory: CVE-2024-36971
Aliases: A-343727534, ASB-A-343727534
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-10
Source: https://osv.dev/vulnerability/CVE-2024-36971
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <4.19.316, >=4.20.0 <5.4.278, >=5.5.0 <5.10.219, >=5.11.0 <5.15.161, >=5.16.0 <6.1.94, >=6.2.0 <6.6.34, >=6.7.0 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: fix __dst_negative_advice() race

__dst_negative_advice() does not enforce proper RCU rules when
sk->dst_cache must be cleared, leading to possible UAF.

RCU rules are that we must first clear sk->sk_dst_cache,
then call dst_release(old_dst).

Note that sk_dst_reset(sk) is implementing this protocol correctly,
while __dst_negative_advice() uses the wrong order.

Given that ip6_negative_advice() has special logic
against RTF_CACHE, this means each of the three ->negative_advice()
existing methods must perform the sk_dst_reset() themselves.

Note the check against NULL dst is centralized in
__dst_negative_advice(), there is no need to duplicate
it in various callbacks.

Many thanks to Clement Lecigne for tracking this issue.

This old bug became visible after the blamed commit, using UDP sockets.

## References
- https://git.kernel.org/stable/c/051c0bde9f0450a2ec3d62a86d2a0d2fad117f13
- https://git.kernel.org/stable/c/2295a7ef5c8c49241bff769e7826ef2582e532a6
- https://git.kernel.org/stable/c/5af198c387128a9d2ddd620b0f0803564a4d4508
- https://git.kernel.org/stable/c/81dd3c82a456b0015461754be7cb2693991421b4
- https://git.kernel.org/stable/c/92f1655aa2b2294d0b49925f3b875a634bd3b59e
- https://git.kernel.org/stable/c/b8af8e6118a6605f0e495a58d591ca94a85a50fc
- https://git.kernel.org/stable/c/db0082825037794c5dba9959c9de13ca34cc5e72
- https://git.kernel.org/stable/c/eacb8b195579c174a6d3e12a9690b206eb7f28cf
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2024-36971
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36971.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36971
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
