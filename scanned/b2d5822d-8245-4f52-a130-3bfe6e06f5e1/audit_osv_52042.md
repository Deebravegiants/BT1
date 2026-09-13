# [H] CVE-2021-46998

## Summary
Severity: High
Advisory: CVE-2021-46998
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-46998
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ethernet:enic: Fix a use after free bug in enic_hard_start_xmit

In enic_hard_start_xmit, it calls enic_queue_wq_skb(). Inside
enic_queue_wq_skb, if some error happens, the skb will be freed
by dev_kfree_skb(skb). But the freed skb is still used in
skb_tx_timestamp(skb).

My patch makes enic_queue_wq_skb() return error and goto spin_unlock()
incase of error. The solution is provided by Govind.
See https://lkml.org/lkml/2021/4/30/961.

## References
- https://git.kernel.org/stable/c/25a87b1f566b5eb2af2857a928f0e2310d900976
- https://git.kernel.org/stable/c/643001b47adc844ae33510c4bb93c236667008a3
- https://git.kernel.org/stable/c/6892396ebf04ea2c021d80e10f4075e014cd7cc3
- https://git.kernel.org/stable/c/7afdd6aba95c8a526038e7abe283eeac3e4320f1
- https://git.kernel.org/stable/c/d90529392aaf498dafa95d212295d64b2cea4e24
- https://git.kernel.org/stable/c/f7f6f07774091a6ddd98500b85386c3c6afb30d3
