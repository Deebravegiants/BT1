# [H] CVE-2022-36123

## Summary
Severity: High
Advisory: CVE-2022-36123
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-07-29
Source: https://osv.dev/vulnerability/CVE-2022-36123
Type: osv

## Details
The Linux kernel before 5.18.13 lacks a certain clear operation for the block starting symbol (.bss). This allows Xen PV guest OS users to cause a denial of service or gain privileges.

## References
- https://security.netapp.com/advisory/ntap-20220901-0003/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.18.13
- https://github.com/torvalds/linux/commit/96e8fc5818686d4a1591bb6907e7fdb64ef29884
- https://sick.codes/sick-2022-128
- https://github.com/sickcodes/security/blob/master/advisories/SICK-2022-128.md
- https://github.com/torvalds/linux/commit/74a0032b8524ee2bd4443128c0bf9775928680b0
