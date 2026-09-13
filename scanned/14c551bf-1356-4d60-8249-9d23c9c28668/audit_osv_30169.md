# [H] ACPI: PRM: Find EFI_MEMORY_RUNTIME block for PRM handler and context

## Summary
Severity: High
Advisory: CVE-2024-50141
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50141
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.171, >=5.16.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ACPI: PRM: Find EFI_MEMORY_RUNTIME block for PRM handler and context

PRMT needs to find the correct type of block to translate the PA-VA
mapping for EFI runtime services.

The issue arises because the PRMT is finding a block of type
EFI_CONVENTIONAL_MEMORY, which is not appropriate for runtime services
as described in Section 2.2.2 (Runtime Services) of the UEFI
Specification [1]. Since the PRM handler is a type of runtime service,
this causes an exception when the PRM handler is called.

    [Firmware Bug]: Unable to handle paging request in EFI runtime service
    WARNING: CPU: 22 PID: 4330 at drivers/firmware/efi/runtime-wrappers.c:341
        __efi_queue_work+0x11c/0x170
    Call trace:

Let PRMT find a block with EFI_MEMORY_RUNTIME for PRM handler and PRM
context.

If no suitable block is found, a warning message will be printed, but
the procedure continues to manage the next PRM handler.

However, if the PRM handler is actually called without proper allocation,
it would result in a failure during error handling.

By using the correct memory types for runtime services, ensure that the
PRM handler and the context are properly mapped in the virtual address
space during runtime, preventing the paging request error.

The issue is really that only memory that has been remapped for runtime
by the firmware can be used by the PRM handler, and so the region needs
to have the EFI_MEMORY_RUNTIME attribute.

[ rjw: Subject and changelog edits ]

## References
- https://git.kernel.org/stable/c/088984c8d54c0053fc4ae606981291d741c5924b
- https://git.kernel.org/stable/c/20e9fafb8bb6f545667d7916b0e81e68c0748810
- https://git.kernel.org/stable/c/795b080d9aa127215a5baf088a22fa09341a0126
- https://git.kernel.org/stable/c/8ce081ad842510f0e70fa6065a401660eac876d4
- https://git.kernel.org/stable/c/8df52929530839e878e6912e33348b54101e3250
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50141.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50141
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
