# [H] CVE-2019-10132

## Summary
Severity: High
Advisory: CVE-2019-10132
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-22
Source: https://osv.dev/vulnerability/CVE-2019-10132
Type: osv

## Details
A vulnerability was found in libvirt >= 4.1.0 in the virtlockd-admin.socket and virtlogd-admin.socket systemd units. A missing SocketMode configuration parameter allows any user on the host to connect using virtlockd-admin-sock or virtlogd-admin-sock and perform administrative tasks against the virtlockd and virtlogd daemons.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5RANC4LWZQRVJGJHVWCU6R4CCXQMDD4L/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CYMNKXAUBZCFBBPFH64FJPH5EJH4GSU2/
- https://usn.ubuntu.com/4021-1/
- https://access.redhat.com/errata/RHSA-2019:1264
- https://access.redhat.com/errata/RHSA-2019:1268
- https://access.redhat.com/errata/RHSA-2019:1455
- https://security.libvirt.org/2019/0003.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10132
