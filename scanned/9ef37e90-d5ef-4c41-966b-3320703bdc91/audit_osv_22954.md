# [M] CVE-2022-4144

## Summary
Severity: Medium
Advisory: CVE-2022-4144
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-11-29
Source: https://osv.dev/vulnerability/CVE-2022-4144
Type: osv

## Details
An out-of-bounds read flaw was found in the QXL display device emulation in QEMU. The qxl_phys2virt() function does not check the size of the structure pointed to by the guest physical address, potentially reading past the end of the bar space into adjacent pages. A malicious guest user could use this flaw to crash the QEMU process on the host causing a denial of service condition.

## References
- https://lists.nongnu.org/archive/html/qemu-devel/2022-11/msg04143.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4144.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GTVPHLLXJ65BUMFBUUZ35F3J632SLFRK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/I7J5IRXJYLELW7D43A75LOWRUE5EU54O/
- https://nvd.nist.gov/vuln/detail/CVE-2022-4144
- https://security.netapp.com/advisory/ntap-20230127-0012/
- https://bugzilla.redhat.com/show_bug.cgi?id=2148506
