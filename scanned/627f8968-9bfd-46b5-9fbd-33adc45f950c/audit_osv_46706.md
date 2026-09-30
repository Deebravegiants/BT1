# [H] CVE-2014-9769

## Summary
Severity: High
Advisory: CVE-2014-9769
CVSS: 7.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2016-03-28
Source: https://osv.dev/vulnerability/CVE-2014-9769
Type: osv

## Details
pcre_jit_compile.c in PCRE 8.35 does not properly use table jumps to optimize nested alternatives, which allows remote attackers to cause a denial of service (stack memory corruption) or possibly have unspecified other impact via a crafted string, as demonstrated by packets encountered by Suricata during use of a regular expression in an Emerging Threats Open ruleset.

## References
- http://vcs.pcre.org/pcre?view=revision&revision=1475
- http://www.openwall.com/lists/oss-security/2016/03/26/1
- http://www.securityfocus.com/bid/85570
- http://www.securitytracker.com/id/1035424
- https://bugs.debian.org/819050
- https://redmine.openinfosecfoundation.org/issues/1693
