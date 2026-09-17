# [H] CVE-2019-13314

## Summary
Severity: High
Advisory: CVE-2019-13314
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-05
Source: https://osv.dev/vulnerability/CVE-2019-13314
Type: osv

## Details
virt-bootstrap 1.1.0 allows local users to discover a root password by listing a process, because this password may be present in the --root-password option to virt_bootstrap.py.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00080.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00026.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/D2PQSLGSTPVQ5WQ4DDKFV4I262JIFXY6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YKMQLYAHCDIE5TBXWDNBG7554KWI5QT3/
- http://www.openwall.com/lists/oss-security/2019/07/08/3
- https://github.com/virt-manager/virt-bootstrap/releases
- https://www.redhat.com/archives/virt-tools-list/2019-July/msg00043.html
