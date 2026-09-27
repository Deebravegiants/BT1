# [M] Libvirt: off-by-one error in udevlistinterfacesbystatus()

## Summary
Severity: Medium
Advisory: CVE-2024-1441
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-11
Source: https://osv.dev/vulnerability/CVE-2024-1441
Type: osv

## Details
An off-by-one error flaw was found in the udevListInterfacesByStatus() function in libvirt when the number of interfaces exceeds the size of the `names` array. This issue can be reproduced by sending specially crafted data to the libvirt daemon, allowing an unprivileged client to perform a denial of service attack by causing the libvirt daemon to crash.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2024/04/msg00000.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/45FFKU3LODT345LAB5T4XZA5WKYMXJYU/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/E6MVZO5GXDB7RHY6MS3ZXES3HPK34P3A/
- https://access.redhat.com/errata/RHSA-2024:2560
- https://access.redhat.com/security/cve/CVE-2024-1441
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1441.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-1441
- https://security.netapp.com/advisory/ntap-20250411-0003/
- https://bugzilla.redhat.com/show_bug.cgi?id=2263841
- https://gitlab.com/libvirt/libvirt/
