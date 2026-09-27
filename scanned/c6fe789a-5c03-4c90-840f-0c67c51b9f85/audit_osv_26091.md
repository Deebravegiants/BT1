# [M] Qemu: improper ide controller reset can lead to mbr overwrite

## Summary
Severity: Medium
Advisory: CVE-2023-5088
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-03
Source: https://osv.dev/vulnerability/CVE-2023-5088
Type: osv

## Details
A bug in QEMU could cause a guest I/O operation otherwise addressed to an arbitrary disk offset to be targeted to offset 0 instead (potentially overwriting the VM's boot code). This could be used, for example, by L2 guests with a virtual disk (vdiskL2) stored on a virtual disk of an L1 (vdiskL1) hypervisor to read and/or write data to LBA 0 of vdiskL1, potentially gaining control of L1 at its next reboot.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2024/03/msg00012.html
- https://lists.debian.org/debian-lts-announce/2025/04/msg00042.html
- https://lore.kernel.org/all/20230921160712.99521-1-simon.rowe@nutanix.com/T/
- https://access.redhat.com/errata/RHSA-2024:2135
- https://access.redhat.com/errata/RHSA-2024:2962
- https://access.redhat.com/security/cve/CVE-2023-5088
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5088.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-5088
- https://security.netapp.com/advisory/ntap-20231208-0005/
- https://bugzilla.redhat.com/show_bug.cgi?id=2247283
