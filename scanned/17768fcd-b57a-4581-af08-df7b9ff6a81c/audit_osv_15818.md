# [H] CVE-2019-19906

## Summary
Severity: High
Advisory: CVE-2019-19906
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-19
Source: https://osv.dev/vulnerability/CVE-2019-19906
Type: osv

## Details
cyrus-sasl (aka Cyrus SASL) 2.1.27 has an out-of-bounds write leading to unauthenticated remote denial-of-service in OpenLDAP via a malformed LDAP packet. The OpenLDAP crash is ultimately caused by an off-by-one error in _sasl_add_string in common.c in cyrus-sasl.

## References
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MW6GZCLECGL2PBNHVNPJIX4RPVRVFR7R/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OB4GSVOJ6ESHQNT5GSV63OX5D4KPSTGT/
- http://seclists.org/fulldisclosure/2020/Jul/23
- http://seclists.org/fulldisclosure/2020/Jul/24
- https://lists.debian.org/debian-lts-announce/2019/12/msg00027.html
- https://seclists.org/bugtraq/2019/Dec/42
- https://support.apple.com/kb/HT211288
- https://support.apple.com/kb/HT211289
- https://www.debian.org/security/2019/dsa-4591
- http://www.openwall.com/lists/oss-security/2022/02/23/4
- https://github.com/cyrusimap/cyrus-sasl/issues/587
- https://usn.ubuntu.com/4256-1/
- https://www.openldap.org/its/index.cgi/Incoming?id=9123
