# [H] crypto: qat - remove unused character device and IOCTLs

## Summary
Severity: High
Advisory: CVE-2026-64529
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64529
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.17.0 <5.10.260, >=5.11.0 <5.15.211, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.37, >=6.19.0 <7.0.14, >=7.1.0 <7.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: qat - remove unused character device and IOCTLs

The QAT driver exposes a character device (qat_adf_ctl) with IOCTLs
for device configuration, start, stop, status query and enumeration.
These IOCTLs are not part of any public uAPI header and have no known
in-tree or out-of-tree users. Device lifecycle is already managed via
sysfs.

The ioctl interface also increases the attack surface and is the
subject of a number of bug reports.

Remove the character device, the IOCTL definitions, and the related
data structures (adf_dev_status_info, adf_user_cfg_key_val,
adf_user_cfg_section, adf_user_cfg_ctl_data). Drop the now-unused
adf_cfg_user.h header and strip adf_ctl_drv.c down to the minimal
module_init/module_exit hooks for workqueue, AER, and crypto/compression
algorithm registration.

Clean up leftover dead code that was only reachable from the removed
IOCTL paths: adf_cfg_del_all(), adf_devmgr_verify_id(),
adf_devmgr_get_num_dev(), adf_devmgr_get_dev_by_id(),
adf_get_vf_real_id() and the unused ADF_CFG macros.

Additionally, drop the entry associated to QAT IOCTLs in
ioctl-number.rst.

## References
- https://git.kernel.org/stable/c/071590a44cbc38483fceb1ab943363ec26868e1b
- https://git.kernel.org/stable/c/1de076f43e64bf65fbe7280a269c70e0e60518df
- https://git.kernel.org/stable/c/3ae49dd04dbb11fb73f17f58a982dba128abe83a
- https://git.kernel.org/stable/c/6848a6e39cac44fdb7cb88f0f777df62172d1551
- https://git.kernel.org/stable/c/a4999664a5ef77bdb0c6e6b935f581ac8ce6b63a
- https://git.kernel.org/stable/c/b1ea97076bd0a5196290deba172034e480646727
- https://git.kernel.org/stable/c/b8ebf008696de1ec08c90d51f94d7e40bd448be1
- https://git.kernel.org/stable/c/d237230728c567297f2f98b425d63156ab2ed17f
- https://git.kernel.org/stable/c/de2cc38489b629927910b1aeff69bba7bd5c6f1b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64529.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64529
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
