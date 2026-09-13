# [H] net: usb: ax88179_178a: fix skb leak in ax88179_tx_fixup()

## Summary
Severity: High
Advisory: CVE-2026-74678
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74678
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: usb: ax88179_178a: fix skb leak in ax88179_tx_fixup()

When the interface has NETIF_F_SG enabled and skb_linearize() fails in
ax88179_tx_fixup(), the function returns NULL without freeing the skb.

usbnet_start_xmit() treats a NULL return from tx_fixup() as a drop
(info->flags does not set FLAG_MULTI_PACKET for this driver), jumping
to the "drop" label where it does `if (skb) dev_kfree_skb_any(skb)`.
Because tx_fixup() returned NULL, the local skb variable in
usbnet_start_xmit() is NULL, so the original skb is never freed — a
memory leak on every TX frame whose linearization fails (i.e. under
memory pressure).

Free the skb before returning, matching the error handling already used
for the pskb_expand_head() failure path in the same function.

## References
- https://git.kernel.org/stable/c/1c63303659a2264bd55d9813df74cb4caeed5922
- https://git.kernel.org/stable/c/1f428e30947395d9b9aacee03e25a4e6cfcad7a4
- https://git.kernel.org/stable/c/2be5091fa693b9119ad25a8bb8c149d236a23ade
- https://git.kernel.org/stable/c/4039cd807a5a46dc5f7618fffae926b8ad8455eb
- https://git.kernel.org/stable/c/58733b1dd46bb231d9d279c132a20ee46da1b664
- https://git.kernel.org/stable/c/83a765cbd7b4d11b0b9fa1bb9d941ae911a2159b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74678.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74678
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
