# [H] tap: add missing verification for short frame

## Summary
Severity: High
Advisory: CVE-2024-41090
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41090
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.4.281, >=5.5.0 <5.10.223, >=5.11.0 <5.15.164, >=5.16.0 <6.1.102, >=6.2.0 <6.6.43, >=6.7.0 <6.9.12, >=6.10.0 <6.10.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

tap: add missing verification for short frame

The cited commit missed to check against the validity of the frame length
in the tap_get_user_xdp() path, which could cause a corrupted skb to be
sent downstack. Even before the skb is transmitted, the
tap_get_user_xdp()-->skb_set_network_header() may assume the size is more
than ETH_HLEN. Once transmitted, this could either cause out-of-bound
access beyond the actual length, or confuse the underlayer with incorrect
or inconsistent header length in the skb metadata.

In the alternative path, tap_get_user() already prohibits short frame which
has the length less than Ethernet header size from being transmitted.

This is to drop any frame shorter than the Ethernet header size just like
how tap_get_user() does.

CVE: CVE-2024-41090

## References
- https://git.kernel.org/stable/c/73d462a38d5f782b7c872fe9ae8393d9ef5483da
- https://git.kernel.org/stable/c/7431144b406ae82807eb87d8c98e518475b0450f
- https://git.kernel.org/stable/c/8be915fc5ff9a5e296f6538be12ea75a1a93bdea
- https://git.kernel.org/stable/c/aa6a5704cab861c9b2ae9f475076e1881e87f5aa
- https://git.kernel.org/stable/c/e1a786b9bbb767fd1c922d424aaa8078cc542309
- https://git.kernel.org/stable/c/e5e5e63c506b93b89b01f522b6a7343585f784e6
- https://git.kernel.org/stable/c/ed7f2afdd0e043a397677e597ced0830b83ba0b3
- https://git.kernel.org/stable/c/ee93e6da30377cf2a75e16cd32bb9fcd86a61c46
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41090.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41090
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
