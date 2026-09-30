# [H] misc: fastrpc: Don't remove map on creater_process and device_release

## Summary
Severity: High
Advisory: CVE-2022-48873
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-21
Source: https://osv.dev/vulnerability/CVE-2022-48873
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.4.230, >=5.5.0 <5.10.165, >=5.11.0 <5.15.90, >=5.16.0 <6.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: fastrpc: Don't remove map on creater_process and device_release

Do not remove the map from the list on error path in
fastrpc_init_create_process, instead call fastrpc_map_put, to avoid
use-after-free. Do not remove it on fastrpc_device_release either,
call fastrpc_map_put instead.

The fastrpc_free_map is the only proper place to remove the map.
This is called only after the reference count is 0.

## References
- https://git.kernel.org/stable/c/193cd853145b63e670bd73740250983af1475330
- https://git.kernel.org/stable/c/1b7b7bb400dd13dcb03fc6e591bb7ca4664bbec8
- https://git.kernel.org/stable/c/35ddd482345c43d9eec1f3406c0f20a95ed4054b
- https://git.kernel.org/stable/c/4b5c44e924a571d0ad07054de549624fbc04e4d7
- https://git.kernel.org/stable/c/5bb96c8f9268e2fdb0e5321cbc358ee5941efc15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48873.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48873
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
