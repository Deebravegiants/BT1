# [H] misc: microchip: pci1xxxx: fix double free in the error handling of gp_aux_bus_probe()

## Summary
Severity: High
Advisory: CVE-2024-36973
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-17
Source: https://osv.dev/vulnerability/CVE-2024-36973
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.95, >=6.2.0 <6.6.35, >=6.7.0 <6.9.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: microchip: pci1xxxx: fix double free in the error handling of gp_aux_bus_probe()

When auxiliary_device_add() returns error and then calls
auxiliary_device_uninit(), callback function
gp_auxiliary_device_release() calls ida_free() and
kfree(aux_device_wrapper) to free memory. We should't
call them again in the error handling path.

Fix this by skipping the redundant cleanup functions.

## References
- https://git.kernel.org/stable/c/086c6cbcc563c81d55257f9b27e14faf1d0963d3
- https://git.kernel.org/stable/c/1efe551982297924d05a367aa2b6ec3d275d5742
- https://git.kernel.org/stable/c/34ae447b138680b5ed3660f7d935ff3faf88ba1a
- https://git.kernel.org/stable/c/86c9713602f786f441630c4ee02891987f8618b9
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36973.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36973
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
