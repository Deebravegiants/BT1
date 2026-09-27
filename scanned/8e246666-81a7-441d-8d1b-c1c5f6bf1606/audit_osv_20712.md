# [M] CVE-2021-3638

## Summary
Severity: Medium
Advisory: CVE-2021-3638
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-03-03
Source: https://osv.dev/vulnerability/CVE-2021-3638
Type: osv

## Details
An out-of-bounds memory access flaw was found in the ATI VGA device emulation of QEMU. This flaw occurs in the ati_2d_blt() routine while handling MMIO write operations when the guest provides invalid values for the destination display parameters. A malicious guest could use this flaw to crash the QEMU process on the host, resulting in a denial of service.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GTVPHLLXJ65BUMFBUUZ35F3J632SLFRK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/I7J5IRXJYLELW7D43A75LOWRUE5EU54O/
- https://security.netapp.com/advisory/ntap-20220407-0003/
- https://ubuntu.com/security/CVE-2021-3638
- https://bugzilla.redhat.com/show_bug.cgi?id=1979858
- https://lists.nongnu.org/archive/html/qemu-devel/2021-09/msg01682.html
