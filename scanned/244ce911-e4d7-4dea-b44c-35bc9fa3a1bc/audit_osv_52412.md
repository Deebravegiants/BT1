# [M] CVE-2021-47421

## Summary
Severity: Medium
Advisory: CVE-2021-47421
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47421
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: handle the case of pci_channel_io_frozen only in amdgpu_pci_resume

In current code, when a PCI error state pci_channel_io_normal is detectd,
it will report PCI_ERS_RESULT_CAN_RECOVER status to PCI driver, and PCI
driver will continue the execution of PCI resume callback report_resume by
pci_walk_bridge, and the callback will go into amdgpu_pci_resume
finally, where write lock is releasd unconditionally without acquiring
such lock first. In this case, a deadlock will happen when other threads
start to acquire the read lock.

To fix this, add a member in amdgpu_device strucutre to cache
pci_channel_state, and only continue the execution in amdgpu_pci_resume
when it's pci_channel_io_frozen.

## References
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://git.kernel.org/stable/c/248b061689a40f4fed05252ee2c89f87cf26d7d8
- https://git.kernel.org/stable/c/72e9a1bf9b722628c28092e0c2cd8717edd201dc
- https://git.kernel.org/stable/c/785cc093b6b5a93cc350421a55f3f1eda6585156
