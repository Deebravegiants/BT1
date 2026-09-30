# [H] CVE-2018-16585

## Summary
Severity: High
Advisory: CVE-2018-16585
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-06
Source: https://osv.dev/vulnerability/CVE-2018-16585
Type: osv

## Details
An issue was discovered in Artifex Ghostscript before 9.24. The .setdistillerkeys PostScript command is accepted even though it is not intended for use during document processing (e.g., after the startup phase). This leads to memory corruption, allowing remote attackers able to supply crafted PostScript to crash the interpreter or possibly have unspecified other impact. Note: A reputable source believes that the CVE is potentially a duplicate of CVE-2018-15910 as explained in Red Hat bugzilla (https://bugzilla.redhat.com/show_bug.cgi?id=1626193)

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=1497d65039885a52b598b137dd8622bd4672f9be
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=971472c83a345a16dac9f90f91258bb22dd77f22
- https://lists.debian.org/debian-lts-announce/2018/09/msg00015.html
- https://security.gentoo.org/glsa/201811-12
- https://usn.ubuntu.com/3768-1/
- https://www.debian.org/security/2018/dsa-4288
- https://bugzilla.redhat.com/show_bug.cgi?id=1626193
- https://seclists.org/oss-sec/2018/q3/182
