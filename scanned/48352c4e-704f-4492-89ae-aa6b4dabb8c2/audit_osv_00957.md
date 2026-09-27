# [C] ALPINE-CVE-2018-12892

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-12892
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.9 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-07-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-12892
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=4.7.0 <4.11.0-r0
- Alpine:v3.11: `xen` — affected >=4.7.0 <4.11.0-r0
- Alpine:v3.12: `xen` — affected >=4.7.0 <4.11.0-r0
- Alpine:v3.13: `xen` — affected >=4.7.0 <4.11.0-r0
- Alpine:v3.14: `xen` — affected >=4.7.0 <4.11.0-r0
- Alpine:v3.15: `xen` — affected >=4.7.0 <4.11.0-r0
- Alpine:v3.16: `xen` — affected >=4.7.0 <4.11.0-r0
- Alpine:v3.17: `xen` — affected >=4.7.0 <4.11.0-r0
- Alpine:v3.18: `xen` — affected >=4.7.0 <4.11.0-r0
- Alpine:v3.19: `xen` — affected >=4.7.0 <4.11.0-r0
- Alpine:v3.20: `xen` — affected >=4.7.0 <4.11.0-r0
- Alpine:v3.21: `xen` — affected >=4.7.0 <4.11.0-r0
- Alpine:v3.22: `xen` — affected >=4.7.0 <4.11.0-r0
- Alpine:v3.23: `xen` — affected >=4.7.0 <4.11.0-r0
- Alpine:v3.24: `xen` — affected >=4.7.0 <4.11.0-r0
- Alpine:v3.5: `xen` — affected >=4.7.0 <4.7.6-r0
- Alpine:v3.6: `xen` — affected >=4.7.0 <4.8.4-r0
- Alpine:v3.7: `xen` — affected >=4.7.0 <4.9.3-r0
- Alpine:v3.8: `xen` — affected >=4.7.0 <4.10.1-r3
- Alpine:v3.9: `xen` — affected >=4.7.0 <4.11.0-r0

## Details
An issue was discovered in Xen 4.7 through 4.10.x. libxl fails to pass the readonly flag to qemu when setting up a SCSI disk, due to what was probably an erroneous merge conflict resolution. Malicious guest administrators or (in some situations) users may be able to write to supposedly read-only disk images. Only emulated SCSI disks (specified as "sd" in the libxl disk configuration, or an equivalent) are affected. IDE disks ("hd") are not affected (because attempts to make them readonly are rejected). Additionally, CDROM devices (that is, devices specified to be presented to the guest as CDROMs, regardless of the nature of the backing storage on the host) are not affected; they are always read only. Only systems using qemu-xen (rather than qemu-xen-traditional) as the device model version are vulnerable. Only systems using libxl or libxl-based toolstacks are vulnerable. (This includes xl, and libvirt with the libxl driver.) The vulnerability is present in Xen versions 4.7 and later. (In earlier versions, provided that the patch for XSA-142 has been applied, attempts to create read only disks are rejected.) If the host and guest together usually support PVHVM, the issue is exploitable only if the malicious guest administrator has control of the guest kernel or guest kernel command line.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-12892
