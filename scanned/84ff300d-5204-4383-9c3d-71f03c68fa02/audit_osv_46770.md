# [H] CVE-2015-20107

## Summary
Severity: High
Advisory: CVE-2015-20107
Aliases: PSF-2022-1
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L)
Published: 2022-04-13
Source: https://osv.dev/vulnerability/CVE-2015-20107
Type: osv

## Details
In Python (aka CPython) up to 3.10.8, the mailcap module does not add escape characters into commands discovered in the system mailcap file. This may allow attackers to inject shell commands into applications that call mailcap.findmatch with untrusted input (if they lack validation of user-provided filenames or arguments). The fix is also back-ported to 3.7, 3.8, 3.9

## References
- https://bugs.python.org/issue24778
- https://github.com/python/cpython/issues/68966
- https://python-security.readthedocs.io/vuln/mailcap-shell-injection.html
- https://security.gentoo.org/glsa/202305-02
- https://security.netapp.com/advisory/ntap-20220616-0001/
- https://bugs.python.org/issue24778
- https://python-security.readthedocs.io/vuln/mailcap-shell-injection.html
- https://bugs.python.org/issue24778
- https://github.com/python/cpython/issues/68966
- https://lists.debian.org/debian-lts-announce/2023/05/msg00024.html
- https://lists.debian.org/debian-lts-announce/2023/06/msg00039.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/46KWPTI72SSEOF53DOYQBQOCN4QQB2GE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/53TQZFLS6O3FLIMVSXFEEPZSWLDZLBOX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/57NECACX333A3BBZM2TR2VZ4ZE3UG3SN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5DBVY4YC2P6EPZZ2DROOXHDOWZ4BJFLW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6QIKVSW3H6W2GQGDE5DTIWLGFNH6KKEW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AKGMYDVKI3XNM27B6I6RQ6QV3TVJAUCG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ERYMM2QVDPOJLX4LYXWYIQN5FOIJLDRY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/F3LNY2NHM6J22O6Q5ANOE3SZRK3OACKR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FCIO2W4DUVVMI6L52QCC4TT2B3K5VWHS/
