# [M] CVE-2022-2308

## Summary
Severity: Medium
Advisory: CVE-2022-2308
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2022-09-01
Source: https://osv.dev/vulnerability/CVE-2022-2308
Type: osv

## Details
A flaw was found in vDPA with VDUSE backend. There are currently no checks in VDUSE kernel driver to ensure the size of the device config space is in line with the features advertised by the VDUSE userspace application. In case of a mismatch, Virtio drivers config read helpers do not initialize the memory indirectly passed to vduse_vdpa_get_config() returning uninitialized memory from the stack. This could cause undefined behavior or data leaks in Virtio drivers.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2103900
- https://bugzilla.redhat.com/show_bug.cgi?id=2103900
