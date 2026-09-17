# [H] scsi: sg: Allow waiting for commands to complete on removed device

## Summary
Severity: High
Advisory: CVE-2022-50215
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50215
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <4.9.326, >=4.10.0 <4.14.291, >=4.15.0 <4.19.256, >=4.20.0 <5.4.211, >=5.5.0 <5.10.137, >=5.11.0 <5.15.61, >=5.16.0 <5.18.18, >=5.19.0 <5.19.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: sg: Allow waiting for commands to complete on removed device

When a SCSI device is removed while in active use, currently sg will
immediately return -ENODEV on any attempt to wait for active commands that
were sent before the removal.  This is problematic for commands that use
SG_FLAG_DIRECT_IO since the data buffer may still be in use by the kernel
when userspace frees or reuses it after getting ENODEV, leading to
corrupted userspace memory (in the case of READ-type commands) or corrupted
data being sent to the device (in the case of WRITE-type commands).  This
has been seen in practice when logging out of a iscsi_tcp session, where
the iSCSI driver may still be processing commands after the device has been
marked for removal.

Change the policy to allow userspace to wait for active sg commands even
when the device is being removed.  Return -ENODEV only when there are no
more responses to read.

## References
- https://git.kernel.org/stable/c/03d8241112d5e3cccce1a01274a221099f07d2e1
- https://git.kernel.org/stable/c/3455607fd7be10b449f5135c00dc306b85dc0d21
- https://git.kernel.org/stable/c/35e60ec39e862159cb92923eefd5230d4a873cb9
- https://git.kernel.org/stable/c/408bfa1489a3cfe7150b81ab0b0df99b23dd5411
- https://git.kernel.org/stable/c/8c004b7dbb340c1e5889f5fb9e5baa6f6e5303e8
- https://git.kernel.org/stable/c/bbc118acf7baf9e93c5e1314d14f481301af4d0f
- https://git.kernel.org/stable/c/ed9afd967cbfe7da2dc0d5e52c62a778dfe9f16b
- https://git.kernel.org/stable/c/f135c65085eed869d10e4e7923ce1015288618da
- https://git.kernel.org/stable/c/f5e61d9b4a699dd16f32d5f39eb1cf98d84c92ed
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50215.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50215
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
