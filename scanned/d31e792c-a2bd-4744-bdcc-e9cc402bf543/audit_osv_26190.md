# [H] hisi_acc_vfio_pci: Update migration data pointer correctly on saving/resume

## Summary
Severity: High
Advisory: CVE-2023-52453
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-02-23
Source: https://osv.dev/vulnerability/CVE-2023-52453
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.14, >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

hisi_acc_vfio_pci: Update migration data pointer correctly on saving/resume

When the optional PRE_COPY support was added to speed up the device
compatibility check, it failed to update the saving/resuming data
pointers based on the fd offset. This results in migration data
corruption and when the device gets started on the destination the
following error is reported in some cases,

[  478.907684] arm-smmu-v3 arm-smmu-v3.2.auto: event 0x10 received:
[  478.913691] arm-smmu-v3 arm-smmu-v3.2.auto:  0x0000310200000010
[  478.919603] arm-smmu-v3 arm-smmu-v3.2.auto:  0x000002088000007f
[  478.925515] arm-smmu-v3 arm-smmu-v3.2.auto:  0x0000000000000000
[  478.931425] arm-smmu-v3 arm-smmu-v3.2.auto:  0x0000000000000000
[  478.947552] hisi_zip 0000:31:00.0: qm_axi_rresp [error status=0x1] found
[  478.955930] hisi_zip 0000:31:00.0: qm_db_timeout [error status=0x400] found
[  478.955944] hisi_zip 0000:31:00.0: qm sq doorbell timeout in function 2

## References
- https://git.kernel.org/stable/c/45f80b2f230df10600e6fa1b83b28bf1c334185e
- https://git.kernel.org/stable/c/6bda81e24a35a856f58e6a5786de579b07371603
- https://git.kernel.org/stable/c/be12ad45e15b5ee0e2526a50266ba1d295d26a88
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52453.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52453
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
