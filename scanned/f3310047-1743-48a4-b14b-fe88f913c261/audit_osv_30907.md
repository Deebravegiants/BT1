# [H] ionic: Fix netdev notifier unregister on failure

## Summary
Severity: High
Advisory: CVE-2024-56715
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56715
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.15.176, >=5.16.0 <6.1.122, >=6.2.0 <6.6.68, >=6.7.0 <6.12.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ionic: Fix netdev notifier unregister on failure

If register_netdev() fails, then the driver leaks the netdev notifier.
Fix this by calling ionic_lif_unregister() on register_netdev()
failure. This will also call ionic_lif_unregister_phc() if it has
already been registered.

## References
- https://git.kernel.org/stable/c/87847938f5708b2509b279369c96572254bcf2ba
- https://git.kernel.org/stable/c/9590d32e090ea2751e131ae5273859ca22f5ac14
- https://git.kernel.org/stable/c/da5736f516a664a9e1ff74902663c64c423045d2
- https://git.kernel.org/stable/c/da93a12876f8b969df7316dc93aac7e725f88252
- https://git.kernel.org/stable/c/ee2e931b2b46de9af7f681258e8ec8e2cd81cfc6
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56715.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56715
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
