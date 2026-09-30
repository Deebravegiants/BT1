# [H] arm64: dts: qcom: monaco: Reserve full Gunyah metadata region

## Summary
Severity: High
Advisory: CVE-2026-43347
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43347
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.24, >=6.19.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64: dts: qcom: monaco: Reserve full Gunyah metadata region

We observe spurious "Synchronous External Abort" exceptions
(ESR=0x96000010) and kernel crashes on Monaco-based platforms.
These faults are caused by the kernel inadvertently accessing
hypervisor-owned memory that is not properly marked as reserved.

>From boot log, The Qualcomm hypervisor reports the memory range
at 0x91a80000 of size 0x80000 (512 KiB) as hypervisor-owned:
qhee_hyp_assign_remove_memory: 0x91a80000/0x80000 -> ret 0

However, the EFI memory map provided by firmware only reserves the
subrange 0x91a40000–0x91a87fff (288 KiB). The remaining portion
(0x91a88000–0x91afffff) is incorrectly reported as conventional
memory (from efi debug):
efi:   0x000091a40000-0x000091a87fff [Reserved...]
efi:   0x000091a88000-0x0000938fffff [Conventional...]

As a result, the allocator may hand out PFNs inside the hypervisor
owned region, causing fatal aborts when the kernel accesses those
addresses.

Add a reserved-memory carveout for the Gunyah hypervisor metadata
at 0x91a80000 (512 KiB) and mark it as no-map so Linux does not
map or allocate from this area.

For the record:
Hyp version: gunyah-e78adb36e debug (2025-11-17 05:38:05 UTC)
UEFI Ver: 6.0.260122.BOOT.MXF.1.0.c1-00449-KODIAKLA-1

## References
- https://git.kernel.org/stable/c/59bd9088336d2bb7e713dcf4df5cbda86bb3c611
- https://git.kernel.org/stable/c/85d98669fa7f1d3041d962515e45ee6e392db6f8
- https://git.kernel.org/stable/c/edde62571f7602d83243ca51729ce42d22ea04d2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43347.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43347
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
