# [H] CVE-2019-1010057

## Summary
Severity: High
Advisory: CVE-2019-1010057
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-16
Source: https://osv.dev/vulnerability/CVE-2019-1010057
Type: osv

## Details
nfdump 1.6.16 and earlier is affected by: Buffer Overflow. The impact is: The impact could range from a denial of service to local code execution. The component is: nfx.c:546, nffile_inline.c:83, minilzo.c (redistributed). The attack vector is: nfdump must read and process a specially crafted file. The fixed version is: after commit 9f0fe9563366f62a71d34c92229da3432ec5cf0e.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ULSZMKA7P7REJMANVL7D6WMZ2L7IRSET/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YTONOGJU5FSMFNRCT6OHXYUMDRKH4RPA/
- https://lists.debian.org/debian-lts-announce/2020/09/msg00021.html
- https://security.gentoo.org/glsa/202003-17
- https://github.com/phaag/nfdump/issues/104
