# [C] CVE-2017-8786

## Summary
Severity: Critical
Advisory: CVE-2017-8786
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-05
Source: https://osv.dev/vulnerability/CVE-2017-8786
Type: osv

## Details
pcre2test.c in PCRE2 10.23 allows remote attackers to cause a denial of service (heap-based buffer overflow) or possibly have unspecified other impact via a crafted regular expression.

## References
- https://security.gentoo.org/glsa/201710-09
- https://bugs.exim.org/show_bug.cgi?id=2079
- https://blogs.gentoo.org/ago/2017/04/29/libpcre-heap-based-buffer-overflow-write-in-pcre2test-c/
- https://vcs.pcre.org/pcre2?view=revision&revision=696
- https://vcs.pcre.org/pcre2?view=revision&revision=697
