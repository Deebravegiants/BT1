# [C] CVE-2016-10152

## Summary
Severity: Critical
Advisory: CVE-2016-10152
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-28
Source: https://osv.dev/vulnerability/CVE-2016-10152
Type: osv

## Details
The read_config_file function in lib/hesiod.c in Hesiod 3.2.1 falls back to the ".athena.mit.edu" default domain when opening the configuration file fails, which allows remote attackers to gain root privileges by poisoning the DNS cache.

## References
- http://www.securityfocus.com/bid/90952
- https://security.gentoo.org/glsa/201805-01
- https://bugzilla.redhat.com/show_bug.cgi?id=1332493
- http://www.openwall.com/lists/oss-security/2017/01/21/1
- https://github.com/achernya/hesiod/pull/10
