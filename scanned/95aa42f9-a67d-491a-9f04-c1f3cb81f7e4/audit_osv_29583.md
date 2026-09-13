# [H] Qemu-kvm: 'qemu-img info' leads to host file read/write

## Summary
Severity: High
Advisory: CVE-2024-4467
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-02
Source: https://osv.dev/vulnerability/CVE-2024-4467
Type: osv

## Details
A flaw was found in the QEMU disk image utility (qemu-img) 'info' command. A specially crafted image file containing a `json:{}` value describing block devices in QMP could cause the qemu-img process on the host to consume large amounts of memory or CPU time, leading to denial of service or read/write to an existing external file.

## References
- http://www.openwall.com/lists/oss-security/2024/07/23/2
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2024:4276
- https://access.redhat.com/errata/RHSA-2024:4277
- https://access.redhat.com/errata/RHSA-2024:4278
- https://access.redhat.com/errata/RHSA-2024:4372
- https://access.redhat.com/errata/RHSA-2024:4373
- https://access.redhat.com/errata/RHSA-2024:4374
- https://access.redhat.com/errata/RHSA-2024:4420
- https://access.redhat.com/errata/RHSA-2024:4724
- https://access.redhat.com/errata/RHSA-2024:4727
- https://access.redhat.com/security/cve/CVE-2024-4467
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/4xxx/CVE-2024-4467.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-4467
- https://security.netapp.com/advisory/ntap-20240822-0005/
- https://bugzilla.redhat.com/show_bug.cgi?id=2278875
- https://gitlab.com/qemu-project/qemu
