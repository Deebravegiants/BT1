# [M] CVE-2023-51764

## Summary
Severity: Medium
Advisory: CVE-2023-51764
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-12-24
Source: https://osv.dev/vulnerability/CVE-2023-51764
Type: osv

## Details
Postfix through 3.8.5 allows SMTP smuggling unless configured with smtpd_data_restrictions=reject_unauth_pipelining and smtpd_discard_ehlo_keywords=chunking (or certain other options that exist in recent versions). Remote attackers can use a published exploitation technique to inject e-mail messages with a spoofed MAIL FROM address, allowing bypass of an SPF protection mechanism. This occurs because Postfix supports <LF>.<CR><LF> but some other popular e-mail servers do not. To prevent attack variants (by always disallowing <LF> without <CR>), a different solution is required, such as the smtpd_forbid_bare_newline=yes option with a Postfix minimum version of 3.5.23, 3.6.13, 3.7.9, 3.8.4, or 3.9.

## References
- https://www.openwall.com/lists/oss-security/2024/01/22/1
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QRLF5SOS7TP5N7FQSEK2NFNB44ISVTZC/
- https://www.postfix.org/announcements/postfix-3.8.5.html
- https://lists.debian.org/debian-lts-announce/2024/01/msg00020.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JQ5WXFCW2N6G2PH3JXDTYW5PH5EBQEGO/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QRLF5SOS7TP5N7FQSEK2NFNB44ISVTZC/
- http://www.openwall.com/lists/oss-security/2024/05/09/3
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JQ5WXFCW2N6G2PH3JXDTYW5PH5EBQEGO/
- https://lwn.net/Articles/956533/
- http://www.openwall.com/lists/oss-security/2023/12/25/1
- http://www.openwall.com/lists/oss-security/2023/12/24/1
- https://access.redhat.com/security/cve/CVE-2023-51764
- https://sec-consult.com/blog/detail/smtp-smuggling-spoofing-e-mails-worldwide/
- https://bugzilla.redhat.com/show_bug.cgi?id=2255563
- https://fahrplan.events.ccc.de/congress/2023/fahrplan/events/11782.html
- https://github.com/eeenvik1/CVE-2023-51764
- https://www.youtube.com/watch?v=V8KPV96g1To
- https://github.com/duy-31/CVE-2023-51764
- https://www.postfix.org/smtp-smuggling.html
