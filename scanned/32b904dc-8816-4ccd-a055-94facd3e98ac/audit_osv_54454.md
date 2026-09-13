# [H] CVE-2023-6535

## Summary
Severity: High
Advisory: CVE-2023-6535
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-07
Source: https://osv.dev/vulnerability/CVE-2023-6535
Type: osv

## Details
A flaw was found in the Linux kernel's NVMe driver. This issue may allow an unauthenticated malicious actor to send a set of crafted TCP packages when using NVMe over TCP, leading the NVMe driver to a NULL pointer dereference in the NVMe driver, causing kernel panic and a denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZFYW6R64GPLUOXSQBJI3JBUX3HGLAYPP/
- https://access.redhat.com/errata/RHSA-2024:0724
- https://access.redhat.com/errata/RHSA-2024:0881
- https://access.redhat.com/errata/RHSA-2024:1248
- https://access.redhat.com/errata/RHSA-2024:3810
- https://access.redhat.com/security/cve/CVE-2023-6535
- https://security.netapp.com/advisory/ntap-20240415-0003/
- https://access.redhat.com/errata/RHSA-2024:0723
- https://access.redhat.com/errata/RHSA-2024:0725
- https://access.redhat.com/errata/RHSA-2024:0897
- https://access.redhat.com/errata/RHSA-2024:2094
- https://bugzilla.redhat.com/show_bug.cgi?id=2254053
