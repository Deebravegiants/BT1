# [M] KVM: Don't null dereference ops->destroy

## Summary
Severity: Medium
Advisory: CVE-2022-49568
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49568
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <5.4.210, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: Don't null dereference ops->destroy

A KVM device cleanup happens in either of two callbacks:
1) destroy() which is called when the VM is being destroyed;
2) release() which is called when a device fd is closed.

Most KVM devices use 1) but Book3s's interrupt controller KVM devices
(XICS, XIVE, XIVE-native) use 2) as they need to close and reopen during
the machine execution. The error handling in kvm_ioctl_create_device()
assumes destroy() is always defined which leads to NULL dereference as
discovered by Syzkaller.

This adds a checks for destroy!=NULL and adds a missing release().

This is not changing kvm_destroy_devices() as devices with defined
release() should have been removed from the KVM devices list by then.

## References
- https://git.kernel.org/stable/c/170465715a60cbb7876e6b961b21bd3225469da8
- https://git.kernel.org/stable/c/3616776bc51cd3262bb1be60cc01c72e0a1959cf
- https://git.kernel.org/stable/c/d4a5a79b780891c5cbdfdc6124d46fdf8d13dba1
- https://git.kernel.org/stable/c/e8bc2427018826e02add7b0ed0fc625a60390ae5
- https://git.kernel.org/stable/c/e91665fbbf3ccb268b268a7d71a6513538d813ac
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49568.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49568
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
