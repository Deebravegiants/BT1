# [H] CVE-2020-35680

## Summary
Severity: High
Advisory: CVE-2020-35680
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-24
Source: https://osv.dev/vulnerability/CVE-2020-35680
Type: osv

## Details
smtpd/lka_filter.c in OpenSMTPD before 6.8.0p1, in certain configurations, allows remote attackers to cause a denial of service (NULL pointer dereference and daemon crash) via a crafted pattern of client activity, because the filter state machine does not properly maintain the I/O channel between the SMTP engine and the filters layer.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5LKTFBQCHGMVPR4IZWHQIYAPM5J3LN3J/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TYAYXRV2DM5K4RU7RHCDZSA2UF6VCTRC/
- https://www.mail-archive.com/misc%40opensmtpd.org/msg05188.html
- https://poolp.org/posts/2020-12-24/december-2020-opensmtpd-6.8.0p1-released-fixed-several-bugs-proposed-several-diffs-book-is-on-github/
- https://security.gentoo.org/glsa/202105-12
- https://github.com/openbsd/src/commit/6c3220444ed06b5796dedfd53a0f4becd903c0d1
