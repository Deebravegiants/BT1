# [H] CVE-2019-10216

## Summary
Severity: High
Advisory: CVE-2019-10216
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-11-27
Source: https://osv.dev/vulnerability/CVE-2019-10216
Type: osv

## Details
In ghostscript before version 9.50, the .buildfont1 procedure did not properly secure its privileged calls, enabling scripts to bypass `-dSAFER` restrictions. An attacker could abuse this flaw by creating a specially crafted PostScript file that could escalate privileges and access files outside of restricted areas.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=5b85ddd19
- https://security.gentoo.org/glsa/202004-03
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10216
