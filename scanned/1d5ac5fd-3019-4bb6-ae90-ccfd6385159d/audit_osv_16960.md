# [M] CVE-2020-10958

## Summary
Severity: Medium
Advisory: CVE-2020-10958
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2020-05-18
Source: https://osv.dev/vulnerability/CVE-2020-10958
Type: osv

## Details
In Dovecot before 2.3.10.1, a crafted SMTP/LMTP message triggers an unauthenticated use-after-free bug in submission-login, submission, or lmtp, and can lead to a crash under circumstances involving many newlines after a command.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00059.html
- http://packetstormsecurity.com/files/157771/Open-Xchange-Dovecot-2.3.10-Null-Pointer-Dereference-Denial-Of-Service.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TTZN2VW55ZC2AQBGBJMLRJSZIKSB2NS6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VVUWHUUAFPC6XGIXYFIPTNBXLHPNM4W6/
- https://usn.ubuntu.com/4361-1/
- http://www.openwall.com/lists/oss-security/2020/05/18/1
- https://dovecot.org/security
- https://www.debian.org/security/2020/dsa-4690
- https://www.openwall.com/lists/oss-security/2020/05/18/1
- http://seclists.org/fulldisclosure/2020/May/37
