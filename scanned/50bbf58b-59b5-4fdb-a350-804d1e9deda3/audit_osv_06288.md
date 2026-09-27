# [C] BIT-libpython-2021-29921

## Summary
Severity: Critical
Advisory: BIT-libpython-2021-29921
Aliases: BIT-python-2021-29921, BIT-python-min-2021-29921, CVE-2021-29921, PSF-2021-2
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2021-29921
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.9.0 <3.9.5

## Details
In Python before 3,9,5, the ipaddress library mishandles leading zero characters in the octets of an IP address string. This (in some situations) allows attackers to bypass access control that is based on IP addresses.

## References
- https://bugs.python.org/issue36384
- https://docs.python.org/3/library/ipaddress.html
- https://github.com/python/cpython/blob/63298930fb531ba2bb4f23bc3b915dbf1e17e9e1/Misc/NEWS.d/3.8.0a4.rst
- https://github.com/python/cpython/pull/12577
- https://github.com/python/cpython/pull/25099
- https://github.com/sickcodes
- https://github.com/sickcodes/security/blob/master/advisories/SICK-2021-014.md
- https://nvd.nist.gov/vuln/detail/CVE-2021-29921
- https://python-security.readthedocs.io/vuln/ipaddress-ipv4-leading-zeros.html
- https://security.gentoo.org/glsa/202305-02
- https://security.netapp.com/advisory/ntap-20210622-0003/
- https://sick.codes/sick-2021-014
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00000.html
