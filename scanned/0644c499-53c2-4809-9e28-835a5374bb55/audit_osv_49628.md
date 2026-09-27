# [H] CVE-2019-14869

## Summary
Severity: High
Advisory: CVE-2019-14869
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-11-15
Source: https://osv.dev/vulnerability/CVE-2019-14869
Type: osv

## Details
A flaw was found in all versions of ghostscript 9.x before 9.50, where the `.charkeys` procedure, where it did not properly secure its privileged calls, enabling scripts to bypass `-dSAFER` restrictions. An attacker could abuse this flaw by creating a specially crafted PostScript file that could escalate privileges within the Ghostscript and access files outside of restricted areas or execute commands.

## References
- https://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=485904772c5f
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2Q4E3OTDAJRSUCOBTDQO7Y5UTE2FFMLF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HC4REO73BEJOJAU7NHFHJECAUAYJUE3H/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IX55AEDERTDFEZAROKZW64MZRPLINEGI/
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00049.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00050.html
- https://access.redhat.com/errata/RHSA-2020:0222
- http://jvn.jp/en/jp/JVN52486659/index.html
- https://bugs.ghostscript.com/show_bug.cgi?id=701841
- https://seclists.org/bugtraq/2019/Nov/27
- http://www.openwall.com/lists/oss-security/2019/11/15/1
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14869
