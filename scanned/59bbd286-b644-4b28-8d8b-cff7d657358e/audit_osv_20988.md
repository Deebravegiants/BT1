# [H] CVE-2021-3929

## Summary
Severity: High
Advisory: CVE-2021-3929
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-08-25
Source: https://osv.dev/vulnerability/CVE-2021-3929
Type: osv

## Details
A DMA reentrancy issue was found in the NVM Express Controller (NVME) emulation in QEMU. This CVE is similar to CVE-2021-3750 and, just like it, when the reentrancy write triggers the reset function nvme_ctrl_reset(), data structs will be freed leading to a use-after-free issue. A malicious guest could use this flaw to crash the QEMU process on the host, resulting in a denial of service condition or, potentially, executing arbitrary code within the context of the QEMU process on the host.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XHNN7QJCEQH7AQG5AQP2GEFAQE6K635I/
- https://access.redhat.com/security/cve/CVE-2021-3929
- https://security.netapp.com/advisory/ntap-20250228-0010/
- https://gitlab.com/qemu-project/qemu/-/issues/556
- https://bugzilla.redhat.com/show_bug.cgi?id=2020298
- https://gitlab.com/qemu-project/qemu/-/commit/736b01642d85be832385
- https://gitlab.com/qemu-project/qemu/-/issues/782
