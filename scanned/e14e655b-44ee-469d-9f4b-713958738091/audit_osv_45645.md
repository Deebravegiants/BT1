# [M] JLSEC-2026-16

## Summary
Severity: Medium
Advisory: JLSEC-2026-16
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/JLSEC-2026-16
Type: osv

## Affected
- Julia: `patch_jll` — affected >=0 <2.8.0+0

## Details
In GNU patch through 2.7.6, the following of symlinks is mishandled in certain cases other than input files. This affects inp.c and util.c.

## References
- http://packetstormsecurity.com/files/154124/GNU-patch-Command-Injection-Directory-Traversal.html
- https://git.savannah.gnu.org/cgit/patch.git/commit/?id=dce4683cbbe107a95f1f0d45fabc304acfb5d71a
- https://github.com/irsl/gnu-patch-vulnerabilities
- https://lists.debian.org/debian-lts-announce/2019/07/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SVWWGISFWACROJJPVJJL4UBLVZ7LPOLT/
- https://seclists.org/bugtraq/2019/Aug/29
- https://seclists.org/bugtraq/2019/Jul/54
- https://security.gentoo.org/glsa/201908-22
- https://security.netapp.com/advisory/ntap-20190828-0001/
- https://usn.ubuntu.com/4071-1/
- https://usn.ubuntu.com/4071-2/
- https://www.debian.org/security/2019/dsa-4489
