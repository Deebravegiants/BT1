# [H] net: tls: fix strparser anchor skb leak on offload RX setup failure

## Summary
Severity: High
Advisory: CVE-2026-52974
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52974
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: tls: fix strparser anchor skb leak on offload RX setup failure

When tls_set_device_offload_rx() fails at tls_dev_add(), the error path
calls tls_sw_free_resources_rx() to clean up the SW context that was
initialized by tls_set_sw_offload(). This function calls
tls_sw_release_resources_rx() (which stops the strparser via
tls_strp_stop()) and tls_sw_free_ctx_rx() (which kfrees the context),
but never frees the anchor skb that was allocated by alloc_skb(0) in
tls_strp_init().

Note that tls_sw_free_resources_rx() is exclusively used for this
"failed to start offload" code path, there's no other caller.

The leak did not exist before commit 84c61fe1a75b ("tls: rx: do not use
the standard strparser"), because the standard strparser doesn't try
to pre-allocate an skb.

The normal close path in tls_sk_proto_close() handles cleanup by calling
tls_sw_strparser_done() (which calls tls_strp_done()) after dropping
the socket lock, because tls_strp_done() does cancel_work_sync() and
the strparser work handler takes the socket lock.

## References
- https://git.kernel.org/stable/c/0c9f399b37ce22a5ed94cc51f03ed07ac7f38e32
- https://git.kernel.org/stable/c/3c405dfa9619e506e75b8e41f8b29a5b99731877
- https://git.kernel.org/stable/c/58689498ca3384851145a754dbb1d8ed1cf9fb54
- https://git.kernel.org/stable/c/688f12aa44511dd57e448eb670075c6302ad1dc1
- https://git.kernel.org/stable/c/9c54e76f8d6eb11735918777ef0e0509e089557d
- https://git.kernel.org/stable/c/bd07fe6c38b9e44ff3fc02692a53f095c5cc9afc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52974.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52974
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
