# [H] CVE-2017-10790

## Summary
Severity: High
Advisory: CVE-2017-10790
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-02
Source: https://osv.dev/vulnerability/CVE-2017-10790
Type: osv

## Details
The _asn1_check_identifier function in GNU Libtasn1 through 4.12 causes a NULL pointer dereference and crash when reading crafted input that triggers assignment of a NULL value within an asn1_node structure. It may lead to a remote denial of service attack.

## References
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/06/msg00026.html
- https://usn.ubuntu.com/3547-1/
- https://security.gentoo.org/glsa/201710-11
- https://www.debian.org/security/2018/dsa-4106
- https://bugzilla.redhat.com/show_bug.cgi?id=1464141
