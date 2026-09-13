# [M] scsi: snic: Fix possible memory leak if device_add() fails

## Summary
Severity: Medium
Advisory: CVE-2023-53436
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53436
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <4.14.323, >=4.15.0 <4.19.292, >=4.20.0 <5.4.254, >=5.5.0 <5.10.191, >=5.11.0 <5.15.127, >=5.16.0 <6.1.46, >=6.2.0 <6.4.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: snic: Fix possible memory leak if device_add() fails

If device_add() returns error, the name allocated by dev_set_name() needs
be freed. As the comment of device_add() says, put_device() should be used
to give up the reference in the error path. So fix this by calling
put_device(), then the name can be freed in kobject_cleanp().

## References
- https://git.kernel.org/stable/c/41320b18a0e0dfb236dba4edb9be12dba1878156
- https://git.kernel.org/stable/c/461f8ac666fa232afee5ed6420099913ec4e4ba2
- https://git.kernel.org/stable/c/58889d5ad74cbc1c9595db74e13522b58b69b0ec
- https://git.kernel.org/stable/c/7723a5d5d187626c4c640842e522cf4e9e39492e
- https://git.kernel.org/stable/c/789275f7c0544374d40bc8d9c81f96751a41df45
- https://git.kernel.org/stable/c/cea09922f5f75652d55b481ee34011fc7f19868b
- https://git.kernel.org/stable/c/ed0acb1ee2e9322b96611635a9ca9303d15ac76c
- https://git.kernel.org/stable/c/f830968d464f55e11bc9260a132fc77daa266aa3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53436.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53436
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
