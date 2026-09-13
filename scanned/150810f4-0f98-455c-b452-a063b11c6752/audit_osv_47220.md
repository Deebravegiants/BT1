# [H] CVE-2016-1235

## Summary
Severity: High
Advisory: CVE-2016-1235
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-11
Source: https://osv.dev/vulnerability/CVE-2016-1235
Type: osv

## Details
The oarsh script in OAR before 2.5.7 allows remote authenticated users of a cluster to obtain sensitive information and possibly gain privileges via vectors related to OpenSSH options.

## References
- https://raw.githubusercontent.com/oar-team/oar/ce77ffed620fdce94881c9b35064507777c24a1c/debian/patches/004-fix-oarsh-security-issue
- http://www.debian.org/security/2016/dsa-3543
- http://oar.imag.fr/oar_2.5.7
