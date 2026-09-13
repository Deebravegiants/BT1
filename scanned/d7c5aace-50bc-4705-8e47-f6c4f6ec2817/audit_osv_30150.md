# [H] drm/amd: Guard against bad data for ATIF ACPI method

## Summary
Severity: High
Advisory: CVE-2024-50117
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50117
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.229, >=5.11.0 <5.15.170, >=5.16.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd: Guard against bad data for ATIF ACPI method

If a BIOS provides bad data in response to an ATIF method call
this causes a NULL pointer dereference in the caller.

```
? show_regs (arch/x86/kernel/dumpstack.c:478 (discriminator 1))
? __die (arch/x86/kernel/dumpstack.c:423 arch/x86/kernel/dumpstack.c:434)
? page_fault_oops (arch/x86/mm/fault.c:544 (discriminator 2) arch/x86/mm/fault.c:705 (discriminator 2))
? do_user_addr_fault (arch/x86/mm/fault.c:440 (discriminator 1) arch/x86/mm/fault.c:1232 (discriminator 1))
? acpi_ut_update_object_reference (drivers/acpi/acpica/utdelete.c:642)
? exc_page_fault (arch/x86/mm/fault.c:1542)
? asm_exc_page_fault (./arch/x86/include/asm/idtentry.h:623)
? amdgpu_atif_query_backlight_caps.constprop.0 (drivers/gpu/drm/amd/amdgpu/amdgpu_acpi.c:387 (discriminator 2)) amdgpu
? amdgpu_atif_query_backlight_caps.constprop.0 (drivers/gpu/drm/amd/amdgpu/amdgpu_acpi.c:386 (discriminator 1)) amdgpu
```

It has been encountered on at least one system, so guard for it.

(cherry picked from commit c9b7c809b89f24e9372a4e7f02d64c950b07fdee)

## References
- https://git.kernel.org/stable/c/1d7175f9c57b1abf9ecfbdfd53ea760761f52ffe
- https://git.kernel.org/stable/c/234682910971732cd4da96fd95946e296e486b38
- https://git.kernel.org/stable/c/43b4fa6e0e238c6e2662f4fb61d9f51c2785fb1d
- https://git.kernel.org/stable/c/58556dcbd5606a5daccaee73b2130bc16b48e025
- https://git.kernel.org/stable/c/6032287747f874b52dc8b9d7490e2799736e035f
- https://git.kernel.org/stable/c/975ede2a7bec52b5da1428829b3439667c8a234b
- https://git.kernel.org/stable/c/bf58f03931fdcf7b3c45cb76ac13244477a60f44
- https://git.kernel.org/stable/c/cd67af3c1762de4c2483ae4dbdd98f9ea8fa56e3
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50117.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50117
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
