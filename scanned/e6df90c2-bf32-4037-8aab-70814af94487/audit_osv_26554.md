# [C] lwt: Fix return values of BPF xmit ops

## Summary
Severity: Critical
Advisory: CVE-2023-53338
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2023-53338
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.4.257, >=5.5.0 <5.10.195, >=5.11.0 <5.15.132, >=5.16.0 <6.1.53, >=6.2.0 <6.4.16, >=6.5.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

lwt: Fix return values of BPF xmit ops

BPF encap ops can return different types of positive values, such like
NET_RX_DROP, NET_XMIT_CN, NETDEV_TX_BUSY, and so on, from function
skb_do_redirect and bpf_lwt_xmit_reroute. At the xmit hook, such return
values would be treated implicitly as LWTUNNEL_XMIT_CONTINUE in
ip(6)_finish_output2. When this happens, skbs that have been freed would
continue to the neighbor subsystem, causing use-after-free bug and
kernel crashes.

To fix the incorrect behavior, skb_do_redirect return values can be
simply discarded, the same as tc-egress behavior. On the other hand,
bpf_lwt_xmit_reroute returns useful errors to local senders, e.g. PMTU
information. Thus convert its return values to avoid the conflict with
LWTUNNEL_XMIT_CONTINUE.

## References
- https://git.kernel.org/stable/c/065d5f17096ec9161180e2c890afdff4dc6125f2
- https://git.kernel.org/stable/c/29b22badb7a84b783e3a4fffca16f7768fb31205
- https://git.kernel.org/stable/c/65583f9e070db7bece20710cfa2e3daeb0b831d9
- https://git.kernel.org/stable/c/67f8f2bae8e7ac72e09def2b667e44704c4d1ee1
- https://git.kernel.org/stable/c/a97f221651fcdc891166e9bc270e3d9bfa5a0080
- https://git.kernel.org/stable/c/d68c17402442f5f494a2c3ebde5cb82f6aa9160a
- https://git.kernel.org/stable/c/e3f647e4b642f9f6d32795a16f92c116c138d2af
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53338.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53338
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
