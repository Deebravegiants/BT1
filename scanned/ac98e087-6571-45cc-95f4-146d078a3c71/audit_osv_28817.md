# [C] USB: core: Fix access violation during port device removal

## Summary
Severity: Critical
Advisory: CVE-2024-36896
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36896
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

USB: core: Fix access violation during port device removal

Testing with KASAN and syzkaller revealed a bug in port.c:disable_store():
usb_hub_to_struct_hub() can return NULL if the hub that the port belongs to
is concurrently removed, but the function does not check for this
possibility before dereferencing the returned value.

It turns out that the first dereference is unnecessary, since hub->intfdev
is the parent of the port device, so it can be changed easily.  Adding a
check for hub == NULL prevents further problems.

The same bug exists in the disable_show() routine, and it can be fixed the
same way.

## References
- https://git.kernel.org/stable/c/5f1d68ef5ddac27c6b997adccd1c339cef1e6848
- https://git.kernel.org/stable/c/6119ef6517ce501fc548154691abdaf1f954a277
- https://git.kernel.org/stable/c/63533549ff53d24daf47c443dbd43c308afc3434
- https://git.kernel.org/stable/c/a4b46d450c49f32e9d4247b421e58083fde304ce
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36896.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36896
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
