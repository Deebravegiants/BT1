# [C] net: ethernet: mtk_eth_soc: Fix use-after-free in metadata dst teardown

## Summary
Severity: Critical
Advisory: CVE-2026-53247
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53247
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ethernet: mtk_eth_soc: Fix use-after-free in metadata dst teardown

mtk_free_dev() calls metadata_dst_free() which frees the metadata_dst
with kfree() immediately, bypassing the RCU grace period.
In the RX path, skb_dst_set_noref() sets a non-refcounted pointer from
the skb to the metadata_dst. This function requires RCU read-side
protection and the dst must remain valid until all RCU readers complete.
Since metadata_dst_free() calls kfree() directly, a use-after-free can
occur if any skb still holds a noref pointer to the dst when the driver
tears it down.
Replace metadata_dst_free() with dst_release() which properly goes
through the refcount path: when the refcount drops to zero, it schedules
the actual free via call_rcu_hurry(), ensuring all RCU readers have
completed before the memory is freed.

## References
- https://git.kernel.org/stable/c/2d86aeb46d5f69c704065a8c69822582787272a1
- https://git.kernel.org/stable/c/459c6f35c58cf0fd5247e55d73ddaa29571d9b7e
- https://git.kernel.org/stable/c/72775977e89c25c99ee84d2c5baa3f86a8ba5cb4
- https://git.kernel.org/stable/c/80df409e1a483676826a6c66e693dba6ac507751
- https://git.kernel.org/stable/c/e634408d2b0cd939cfe019398a21fb47b7a8ffe3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53247.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53247
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
