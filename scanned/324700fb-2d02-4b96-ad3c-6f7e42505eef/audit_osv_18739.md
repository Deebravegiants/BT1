# [H] CVE-2020-35679

## Summary
Severity: High
Advisory: CVE-2020-35679
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-24
Source: https://osv.dev/vulnerability/CVE-2020-35679
Type: osv

## Details
smtpd/table.c in OpenSMTPD before 6.8.0p1 lacks a certain regfree, which might allow attackers to trigger a "very significant" memory leak via messages to an instance that performs many regex lookups.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5LKTFBQCHGMVPR4IZWHQIYAPM5J3LN3J/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TYAYXRV2DM5K4RU7RHCDZSA2UF6VCTRC/
- https://www.mail-archive.com/misc%40opensmtpd.org/msg05188.html
- https://poolp.org/posts/2020-12-24/december-2020-opensmtpd-6.8.0p1-released-fixed-several-bugs-proposed-several-diffs-book-is-on-github/
- https://security.gentoo.org/glsa/202105-12
- https://github.com/openbsd/src/commit/79a034b4aed29e965f45a13409268290c9910043
