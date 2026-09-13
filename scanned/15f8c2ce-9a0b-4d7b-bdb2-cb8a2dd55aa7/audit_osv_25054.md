# [M] Qemu: e1000e: heap use-after-free in e1000e_write_packet_to_guest()

## Summary
Severity: Medium
Advisory: CVE-2023-3019
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2023-07-24
Source: https://osv.dev/vulnerability/CVE-2023-3019
Type: osv

## Details
A DMA reentrancy issue leading to a use-after-free error was found in the e1000e NIC emulation code in QEMU. This issue could allow a privileged guest user to crash the QEMU process on the host, resulting in a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://cert-portal.siemens.com/productcert/html/ssa-577017.html
- https://lists.debian.org/debian-lts-announce/2025/04/msg00042.html
- https://access.redhat.com/errata/RHSA-2024:0135
- https://access.redhat.com/errata/RHSA-2024:0404
- https://access.redhat.com/errata/RHSA-2024:0569
- https://access.redhat.com/errata/RHSA-2024:2135
- https://access.redhat.com/security/cve/CVE-2023-3019
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3019.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3019
- https://security.netapp.com/advisory/ntap-20230831-0005/
- https://bugzilla.redhat.com/show_bug.cgi?id=2222351
