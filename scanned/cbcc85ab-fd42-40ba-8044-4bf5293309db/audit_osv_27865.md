# [H] thermal: intel: hfi: Add syscore callbacks for system-wide PM

## Summary
Severity: High
Advisory: CVE-2024-26646
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-26
Source: https://osv.dev/vulnerability/CVE-2024-26646
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.76, >=6.2.0 <6.6.15, >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

thermal: intel: hfi: Add syscore callbacks for system-wide PM

The kernel allocates a memory buffer and provides its location to the
hardware, which uses it to update the HFI table. This allocation occurs
during boot and remains constant throughout runtime.

When resuming from hibernation, the restore kernel allocates a second
memory buffer and reprograms the HFI hardware with the new location as
part of a normal boot. The location of the second memory buffer may
differ from the one allocated by the image kernel.

When the restore kernel transfers control to the image kernel, its HFI
buffer becomes invalid, potentially leading to memory corruption if the
hardware writes to it (the hardware continues to use the buffer from the
restore kernel).

It is also possible that the hardware "forgets" the address of the memory
buffer when resuming from "deep" suspend. Memory corruption may also occur
in such a scenario.

To prevent the described memory corruption, disable HFI when preparing to
suspend or hibernate. Enable it when resuming.

Add syscore callbacks to handle the package of the boot CPU (packages of
non-boot CPUs are handled via CPU offline). Syscore ops always run on the
boot CPU. Additionally, HFI only needs to be disabled during "deep" suspend
and hibernation. Syscore ops only run in these cases.

[ rjw: Comment adjustment, subject and changelog edits ]

## References
- https://git.kernel.org/stable/c/019ccc66d56a696a4dfee3bfa2f04d0a7c3d89ee
- https://git.kernel.org/stable/c/28f010dc50df0f7987c04112114fcfa7e0803566
- https://git.kernel.org/stable/c/97566d09fd02d2ab329774bb89a2cdf2267e86d9
- https://git.kernel.org/stable/c/c9d6d63b6c03afaa6f185df249af693a7939577c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26646.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26646
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
