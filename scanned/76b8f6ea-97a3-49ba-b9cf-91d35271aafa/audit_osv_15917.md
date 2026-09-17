# [H] CVE-2019-20454

## Summary
Severity: High
Advisory: CVE-2019-20454
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-14
Source: https://osv.dev/vulnerability/CVE-2019-20454
Type: osv

## Details
An out-of-bounds read was discovered in PCRE before 10.34 when the pattern \X is JIT compiled and used to match specially crafted subjects in non-UTF mode. Applications that use PCRE to parse untrusted input may be vulnerable to this flaw, which would allow an attacker to crash the application. The flaw occurs in do_extuni_no_utf in pcre2_jit_compile.c.

## References
- https://lists.debian.org/debian-lts-announce/2023/03/msg00014.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OQRAHYHLRNMBTPR3KXVM27NSZP3KTOPI/
- https://security.gentoo.org/glsa/202006-16
- https://bugs.exim.org/show_bug.cgi?id=2421
- https://bugs.php.net/bug.php?id=78338
- https://bugzilla.redhat.com/show_bug.cgi?id=1735494
- https://vcs.pcre.org/pcre2?view=revision&revision=1092
