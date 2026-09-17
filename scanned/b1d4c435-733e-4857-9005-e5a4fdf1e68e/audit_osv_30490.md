# [M] usb: dwc3: fix fault at system suspend if device was already runtime suspended

## Summary
Severity: Medium
Advisory: CVE-2024-53070
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53070
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.170 <5.15.172, >=6.1.115 <6.1.117, >=6.6.59 <6.6.61, >=6.11.5 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: dwc3: fix fault at system suspend if device was already runtime suspended

If the device was already runtime suspended then during system suspend
we cannot access the device registers else it will crash.

Also we cannot access any registers after dwc3_core_exit() on some
platforms so move the dwc3_enable_susphy() call to the top.

## References
- https://git.kernel.org/stable/c/06b98197b69e2f2af9cb1991ee0b1c876edf7b86
- https://git.kernel.org/stable/c/4abc5ee334fe4aba50461c45fdaaa4c5e5c57789
- https://git.kernel.org/stable/c/562804b1561cc248cc37746a1c96c83cab1d7209
- https://git.kernel.org/stable/c/9cfb31e4c89d200d8ab7cb1e0bb9e6e8d621ca0b
- https://git.kernel.org/stable/c/d9e65d461a9de037e7c9d584776d025cfce6d86d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53070.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53070
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
