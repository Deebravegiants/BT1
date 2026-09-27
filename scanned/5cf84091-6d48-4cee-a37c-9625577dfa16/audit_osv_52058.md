# [H] CVE-2021-47017

## Summary
Severity: High
Advisory: CVE-2021-47017
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47017
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ath10k: Fix a use after free in ath10k_htc_send_bundle

In ath10k_htc_send_bundle, the bundle_skb could be freed by
dev_kfree_skb_any(bundle_skb). But the bundle_skb is used later
by bundle_skb->len.

As skb_len = bundle_skb->len, my patch replaces bundle_skb->len to
skb_len after the bundle_skb was freed.

## References
- https://git.kernel.org/stable/c/3b1ac40c6012140828caa79e592a438a18ebf71b
- https://git.kernel.org/stable/c/5e413c0831ff4700d1739db3fa3ae9f859744676
- https://git.kernel.org/stable/c/8392df5d7e0b6a7d21440da1fc259f9938f4dec3
- https://git.kernel.org/stable/c/8bb054fb336f4250002fff4e0b075221c05c3c65
