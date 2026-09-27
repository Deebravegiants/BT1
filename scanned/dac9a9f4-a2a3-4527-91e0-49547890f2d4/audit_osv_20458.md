# [M] CVE-2021-33910

## Summary
Severity: Medium
Advisory: CVE-2021-33910
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-20
Source: https://osv.dev/vulnerability/CVE-2021-33910
Type: osv

## Details
basic/unit-name.c in systemd prior to 246.15, 247.8, 248.5, and 249.1 has a Memory Allocation with an Excessive Size Value (involving strdupa and alloca for a pathname controlled by a local attacker) that results in an operating system crash.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-222547.pdf
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2LSDMHAKI4LGFOCSPXNVVSEWQFAVFWR7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/42TMJVNYRY65B4QCJICBYOEIVZV3KUYI/
- https://security.gentoo.org/glsa/202107-48
- https://security.netapp.com/advisory/ntap-20211104-0008/
- https://www.debian.org/security/2021/dsa-4942
- http://www.openwall.com/lists/oss-security/2021/08/04/2
- http://www.openwall.com/lists/oss-security/2021/08/17/3
- http://www.openwall.com/lists/oss-security/2021/09/07/3
- https://github.com/systemd/systemd-stable/commit/4a1c5f34bd3e1daed4490e9d97918e504d19733b
- https://github.com/systemd/systemd-stable/commit/764b74113e36ac5219a4b82a05f311b5a92136ce
- https://github.com/systemd/systemd-stable/commit/b00674347337b7531c92fdb65590ab253bb57538
- https://github.com/systemd/systemd-stable/commit/cfd14c65374027b34dbbc4f0551456c5dc2d1f61
- https://github.com/systemd/systemd/commit/b34a4f0e6729de292cb3b0c03c1d48f246ad896b
- https://github.com/systemd/systemd/pull/20256/commits/441e0115646d54f080e5c3bb0ba477c892861ab9
- http://packetstormsecurity.com/files/163621/Sequoia-A-Deep-Root-In-Linuxs-Filesystem-Layer.html
- https://www.openwall.com/lists/oss-security/2021/07/20/2
