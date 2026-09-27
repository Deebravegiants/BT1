# [H] RDMA/siw: Remove direct link to net_device

## Summary
Severity: High
Advisory: CVE-2024-57857
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-15
Source: https://osv.dev/vulnerability/CVE-2024-57857
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <6.12.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/siw: Remove direct link to net_device

Do not manage a per device direct link to net_device. Rely
on associated ib_devices net_device management, not doubling
the effort locally. A badly managed local link to net_device
was causing a 'KASAN: slab-use-after-free' exception during
siw_query_port() call.

## References
- https://git.kernel.org/stable/c/16b87037b48889d21854c8e97aec8a1baf2642b3
- https://git.kernel.org/stable/c/4eafeb4f021c50d13f199239d913b37de3c83135
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57857.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57857
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
