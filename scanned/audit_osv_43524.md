# [H] vduse: hold vduse_lock across IDR lookup in open path

## Summary
Severity: High
Advisory: CVE-2026-74313
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74313
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

vduse: hold vduse_lock across IDR lookup in open path

vduse_dev_open() looks up struct vduse_dev through the IDR and then
acquires dev->lock only after vduse_lock has been dropped.

This leaves a window where a concurrent VDUSE_DESTROY_DEV can remove the
same object from the IDR and free it before the open path locks the
device, leading to a use-after-free.

Close this race by keeping vduse_lock held until dev->lock has been
acquired in the open path, matching the lock ordering already used by
the destroy path.

## References
- https://git.kernel.org/stable/c/35483c5306e09b3190ff937089d404a78012695c
- https://git.kernel.org/stable/c/5c1560be8aa6849356455af67518d35c551cbd95
- https://git.kernel.org/stable/c/79e12c891940b0c4c75881b7fd82a8cbb8ac97be
- https://git.kernel.org/stable/c/93ed4692f2299a40346025979f40e4a9b7b33af7
- https://git.kernel.org/stable/c/a2d0a57538fd0b3b3ab75d64bb64f4cd2fab13a2
- https://git.kernel.org/stable/c/d94e2947203aead590fd63f667d316d4475d65af
- https://git.kernel.org/stable/c/e440e077748939839d9f76e24383b76b785f80ce
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74313.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74313
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
