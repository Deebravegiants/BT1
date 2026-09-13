# [M] CVE-2020-25678

## Summary
Severity: Medium
Advisory: CVE-2020-25678
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-01-08
Source: https://osv.dev/vulnerability/CVE-2020-25678
Type: osv

## Details
A flaw was found in ceph in versions prior to 16.y.z where ceph stores mgr module passwords in clear text. This can be found by searching the mgr logs for grafana and dashboard, with passwords visible.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00034.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OQTBKVXVYP7GPQNZ5VASOIJHMLK7727M/
- https://security.gentoo.org/glsa/202105-39
- https://bugzilla.redhat.com/show_bug.cgi?id=1892109
- https://tracker.ceph.com/issues/37503
