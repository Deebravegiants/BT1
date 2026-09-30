# [H] acpi: nfit: vmalloc-out-of-bounds Read in acpi_nfit_ctl

## Summary
Severity: High
Advisory: CVE-2024-56662
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56662
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.10.232, >=5.11.0 <5.15.175, >=5.16.0 <6.1.121, >=6.2.0 <6.6.67, >=6.7.0 <6.12.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

acpi: nfit: vmalloc-out-of-bounds Read in acpi_nfit_ctl

Fix an issue detected by syzbot with KASAN:

BUG: KASAN: vmalloc-out-of-bounds in cmd_to_func drivers/acpi/nfit/
core.c:416 [inline]
BUG: KASAN: vmalloc-out-of-bounds in acpi_nfit_ctl+0x20e8/0x24a0
drivers/acpi/nfit/core.c:459

The issue occurs in cmd_to_func when the call_pkg->nd_reserved2
array is accessed without verifying that call_pkg points to a buffer
that is appropriately sized as a struct nd_cmd_pkg. This can lead
to out-of-bounds access and undefined behavior if the buffer does not
have sufficient space.

To address this, a check was added in acpi_nfit_ctl() to ensure that
buf is not NULL and that buf_len is less than sizeof(*call_pkg)
before accessing it. This ensures safe access to the members of
call_pkg, including the nd_reserved2 array.

## References
- https://git.kernel.org/stable/c/143f723e9eb4f0302ffb7adfdc7ef77eab3f68e0
- https://git.kernel.org/stable/c/212846fafb753a48e869e2a342fc1e24048da771
- https://git.kernel.org/stable/c/265e98f72bac6c41a4492d3e30a8e5fd22fe0779
- https://git.kernel.org/stable/c/616aa5f3c86e0479bcbb81e41c08c43ff32af637
- https://git.kernel.org/stable/c/bbdb3307f609ec4dc9558770f464ede01fe52aed
- https://git.kernel.org/stable/c/e08dc2dc3c3f7938df0e4476fe3e6fdec5583c1d
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56662.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56662
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
