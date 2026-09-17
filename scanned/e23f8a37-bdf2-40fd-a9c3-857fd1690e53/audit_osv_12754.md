# [M] CVE-2018-14628

## Summary
Severity: Medium
Advisory: CVE-2018-14628
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-01-17
Source: https://osv.dev/vulnerability/CVE-2018-14628
Type: osv

## Details
An information leak vulnerability was discovered in Samba's LDAP server. Due to missing access control checks, an authenticated but unprivileged attacker could discover the names and preserved attributes of deleted objects in the LDAP store.

## References
- https://security.netapp.com/advisory/ntap-20230223-0008/
- https://bugzilla.redhat.com/show_bug.cgi?id=1625445
- https://bugzilla.samba.org/show_bug.cgi?id=13595
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6DK57HQRTCDOZDIIICYWQ4Z5IQXTWVVW/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ACVMYEP5KJRL3FWSCZW2MQZ26IVPXY62/
- http://www.openwall.com/lists/oss-security/2023/11/28/4
