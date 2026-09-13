# [H] CVE-2021-36386

## Summary
Severity: High
Advisory: CVE-2021-36386
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-30
Source: https://osv.dev/vulnerability/CVE-2021-36386
Type: osv

## Details
report_vbuild in report.c in Fetchmail before 6.4.20 sometimes omits initialization of the vsnprintf va_list argument, which might allow mail servers to cause a denial of service or possibly have unspecified other impact via long error messages. NOTE: it is unclear whether use of Fetchmail on any realistic platform results in an impact beyond an inconvenience to the client user.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AGYO5AHSXTCKA4NQC2Z4H3XMMYNAGC77/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OIXKO6QW3AUHGJVWKJXBCOVBYJUJRBFC/
- https://www.fetchmail.info/security.html
- https://security.gentoo.org/glsa/202209-14
- https://www.fetchmail.info/fetchmail-SA-2021-01.txt
- http://www.openwall.com/lists/oss-security/2021/07/28/5
- http://www.openwall.com/lists/oss-security/2021/08/09/1
