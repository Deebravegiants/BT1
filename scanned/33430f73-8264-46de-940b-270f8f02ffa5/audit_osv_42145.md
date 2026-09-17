# [H] can: esd_usb: kill anchored URBs before freeing netdevs

## Summary
Severity: High
Advisory: CVE-2026-64585
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-64585
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.36 <5.15.217, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: esd_usb: kill anchored URBs before freeing netdevs

esd_usb_disconnect() frees each CAN netdev with free_candev() inside
its per-netdev loop and only calls unlink_all_urbs(dev) afterwards.
The per-netdev private data (struct esd_usb_net_priv) is embedded in
the net_device allocation returned by alloc_candev(), so once
free_candev() has run, dev->nets[i] points to freed memory.
unlink_all_urbs() then dereferences the freed dev->nets[i] to kill the
per-netdev TX anchor (usb_kill_anchored_urbs(&priv->tx_submitted)),
clear active_tx_jobs, and reset priv->tx_contexts[].

Reorder the teardown so the anchored URBs are killed before the netdevs
are freed, matching other CAN/USB drivers in the same directory such as
ems_usb, usb_8dev and mcba_usb, which unregister, then unlink, then
free: unregister the netdevs first (which stops their TX queues), call
unlink_all_urbs(dev) once, then free the netdevs.

This issue was found by an in-house static analysis tool.

## References
- https://git.kernel.org/stable/c/5832c55b3c824ba2fe9c36ac3c411baddcce053e
- https://git.kernel.org/stable/c/765ba1c91823a296447528791b89a6504947fd5c
- https://git.kernel.org/stable/c/a02e1d8f191324583599544d54e59e6a2b74bb0e
- https://git.kernel.org/stable/c/a3314f10369df70925140f59bbe069718f65a0b9
- https://git.kernel.org/stable/c/aa1d005927db38af783c1a4a8a00a39e0229ab2d
- https://git.kernel.org/stable/c/c43122fef328a70045fe7621c06de6b2b8e19264
- https://git.kernel.org/stable/c/d12f6add48f2da15c8c8281961d3faad804c76cf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64585.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64585
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
