# [H] x86/tdx: Fix "in-kernel MMIO" check

## Summary
Severity: High
Advisory: CVE-2024-47727
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47727
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.113, >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/tdx: Fix "in-kernel MMIO" check

TDX only supports kernel-initiated MMIO operations. The handle_mmio()
function checks if the #VE exception occurred in the kernel and rejects
the operation if it did not.

However, userspace can deceive the kernel into performing MMIO on its
behalf. For example, if userspace can point a syscall to an MMIO address,
syscall does get_user() or put_user() on it, triggering MMIO #VE. The
kernel will treat the #VE as in-kernel MMIO.

Ensure that the target MMIO address is within the kernel before decoding
instruction.

## References
- https://git.kernel.org/stable/c/18ecd5b74682839e7cdafb7cd1ec106df7baa18c
- https://git.kernel.org/stable/c/25703a3c980e21548774eea8c8a87a75c5c8f58c
- https://git.kernel.org/stable/c/4c0c5dcb5471de5fc8f0a1c4980e5815339e1cee
- https://git.kernel.org/stable/c/bca2e29f7e26ce7c3522f8b324c0bd85612f68e3
- https://git.kernel.org/stable/c/d4fc4d01471528da8a9797a065982e05090e1d81
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47727.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47727
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
