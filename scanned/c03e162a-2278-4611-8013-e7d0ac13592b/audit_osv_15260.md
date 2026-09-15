# [H] CVE-2019-14844

## Summary
Severity: High
Advisory: CVE-2019-14844
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-26
Source: https://osv.dev/vulnerability/CVE-2019-14844
Type: osv

## Details
A flaw was found in, Fedora versions of krb5 from 1.16.1 to, including 1.17.x, in the way a Kerberos client could crash the KDC by sending one of the RFC 4556 "enctypes". A remote unauthenticated user could use this flaw to crash the KDC.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/54ZYKEJZ77BXZWGF4NEVKC33ESVROEYC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N4LS5PIJOCNOUZGLO2OBT6GY334PUOSW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TDE2QOKK4I4TV4WV74ZQWICZ4HJN2MOK/
- https://security.netapp.com/advisory/ntap-20220325-0003/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14844
- https://github.com/krb5/krb5/pull/981
