# [H] CVE-2020-28196

## Summary
Severity: High
Advisory: CVE-2020-28196
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-06
Source: https://osv.dev/vulnerability/CVE-2020-28196
Type: osv

## Details
MIT Kerberos 5 (aka krb5) before 1.17.2 and 1.18.x before 1.18.3 allows unbounded recursion via an ASN.1-encoded Kerberos message because the lib/krb5/asn.1/asn1_encode.c support for BER indefinite lengths lacks a recursion limit.

## References
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/45KKOZQWIIIW5C45PJVGQ32AXBSYNBE7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/73IGOG6CZAVMVNS4GGRMOLOZ7B6QVA7F/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KPH2V3WSQTELROZK3GFCPQDOFLKIZ6H5/
- https://lists.debian.org/debian-lts-announce/2020/11/msg00011.html
- https://security.gentoo.org/glsa/202011-17
- https://security.netapp.com/advisory/ntap-20201202-0001/
- https://security.netapp.com/advisory/ntap-20210513-0002/
- https://www.debian.org/security/2020/dsa-4795
- https://github.com/krb5/krb5/commit/57415dda6cf04e73ffc3723be518eddfae599bfd
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
