# [H] CVE-2020-27153

## Summary
Severity: High
Advisory: CVE-2020-27153
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2020-10-15
Source: https://osv.dev/vulnerability/CVE-2020-27153
Type: osv

## Details
In BlueZ before 5.55, a double free was found in the gatttool disconnect_cb() routine from shared/att.c. A remote attacker could potentially cause a denial of service or code execution, during service discovery, due to a redundant disconnect MGMT event.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00034.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00036.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00022.html
- https://security.gentoo.org/glsa/202011-01
- https://www.debian.org/security/2021/dsa-4951
- https://bugzilla.redhat.com/show_bug.cgi?id=1884817
- https://github.com/bluez/bluez/commit/1cd644db8c23a2f530ddb93cebed7dacc5f5721a
- https://github.com/bluez/bluez/commit/5a180f2ec9edfacafd95e5fed20d36fe8e077f07
