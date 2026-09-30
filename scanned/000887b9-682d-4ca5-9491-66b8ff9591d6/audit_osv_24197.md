# [M] drivers/md/md-bitmap: check the return value of md_bitmap_get_counter()

## Summary
Severity: Medium
Advisory: CVE-2022-50402
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50402
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.5.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drivers/md/md-bitmap: check the return value of md_bitmap_get_counter()

Check the return value of md_bitmap_get_counter() in case it returns
NULL pointer, which will result in a null pointer dereference.

v2: update the check to include other dereference

## References
- https://git.kernel.org/stable/c/100caacfa0ed26e061954c90cdc835d42f709536
- https://git.kernel.org/stable/c/21e9aac9a74d30907d44bae0d24c036cb3819406
- https://git.kernel.org/stable/c/3bd548e5b819b8c0f2c9085de775c5c7bff9052f
- https://git.kernel.org/stable/c/5d8d046f3dba939e74e2414f009df426700430ed
- https://git.kernel.org/stable/c/99bef41f8e8d1d52b5cb34f2f193f1346192752b
- https://git.kernel.org/stable/c/b621d17fe8b079574c773800148fb86907f3445d
- https://git.kernel.org/stable/c/ff3b7e12bc9f50de05c9d82b5b79e23e5be888f1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50402.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50402
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
