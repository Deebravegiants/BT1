# [M] ASoC: imx-hdmi: Fix refcount leak in imx_hdmi_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49480
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49480
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: imx-hdmi: Fix refcount leak in imx_hdmi_probe

of_find_device_by_node() takes reference, we should use put_device()
to release it. when devm_kzalloc() fails, it doesn't have a
put_device(), it will cause refcount leak.
Add missing put_device() to fix this.

## References
- https://git.kernel.org/stable/c/81b7edaabd44ba133006ad72056914eb36828d60
- https://git.kernel.org/stable/c/8205a0114db10ec41bd2b748cdd7528632082eca
- https://git.kernel.org/stable/c/cf760e494ee5fa6bc2dc222f0098c741ad460801
- https://git.kernel.org/stable/c/ed46731d8e86c8d65f5fc717671e1f1f6c3146d2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49480.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49480
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
