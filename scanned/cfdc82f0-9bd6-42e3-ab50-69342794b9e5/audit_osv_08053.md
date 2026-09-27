# [H] CVE-2016-10151

## Summary
Severity: High
Advisory: CVE-2016-10151
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-01
Source: https://osv.dev/vulnerability/CVE-2016-10151
Type: osv

## Details
The hesiod_init function in lib/hesiod.c in Hesiod 3.2.1 compares EUID with UID to determine whether to use configurations from environment variables, which allows local users to gain privileges via the (1) HESIOD_CONFIG or (2) HES_DOMAIN environment variable and leveraging certain SUID/SGUID binary.

## References
- http://www.securityfocus.com/bid/90952
- https://security.gentoo.org/glsa/201805-01
- https://bugzilla.redhat.com/show_bug.cgi?id=1332508
- http://www.openwall.com/lists/oss-security/2017/01/21/1
- https://github.com/achernya/hesiod/pull/9
