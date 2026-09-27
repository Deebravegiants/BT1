# [M] An integer overflow leading to a heap-buffer overflow was found in The X Input Method (XIM) client...

## Summary
Severity: Medium
Advisory: JLSEC-2026-469
Ecosystem: Julia
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-469
Type: osv

## Affected
- Julia: `Xorg_libX11_jll` — affected >=0 <1.8.6+0

## Details
An integer overflow leading to a heap-buffer overflow was found in The X Input Method (XIM) client was implemented in libX11 before version 1.6.10. As per upstream this is security relevant when setuid programs call XIM client functions while running with elevated privileges. No such programs are shipped with Red Hat Enterprise Linux.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00014.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00024.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00031.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-14344
- https://github.com/advisories/GHSA-g6cq-58wq-v493
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4VDDSAYV7XGNRCXE7HCU23645MG74OFF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7AVXCQOSCAPKYYHFIJAZ6E2C7LJBTLXF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XY4H2SIEF2362AMNX5ZKWAELGU7LKFJB/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4VDDSAYV7XGNRCXE7HCU23645MG74OFF/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7AVXCQOSCAPKYYHFIJAZ6E2C7LJBTLXF/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XY4H2SIEF2362AMNX5ZKWAELGU7LKFJB/
- https://lists.x.org/archives/xorg-announce/2020-July/003050.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-14344
- https://security.gentoo.org/glsa/202008-18
- https://usn.ubuntu.com/4487-1/
- https://usn.ubuntu.com/4487-2/
- https://www.openwall.com/lists/oss-security/2020/07/31/1
