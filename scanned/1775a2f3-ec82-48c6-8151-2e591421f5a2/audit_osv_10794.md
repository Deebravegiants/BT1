# [H] CVE-2017-2669

## Summary
Severity: High
Advisory: CVE-2017-2669
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-21
Source: https://osv.dev/vulnerability/CVE-2017-2669
Type: osv

## Details
Dovecot before version 2.2.29 is vulnerable to a denial of service. When 'dict' passdb and userdb were used for user authentication, the username sent by the IMAP/POP3 client was sent through var_expand() to perform %variable expansion. Sending specially crafted %variable fields could result in excessive memory usage causing the process to crash (and restart), or excessive CPU usage causing all authentications to hang.

## References
- http://www.openwall.com/lists/oss-security/2017/04/11/1
- http://www.securityfocus.com/bid/97536
- https://dovecot.org/pipermail/dovecot-news/2017-April/000341.html
- https://github.com/dovecot/core/commit/000030feb7a30f193197f1aab8a7b04a26b42735.patch
- https://www.debian.org/security/2017/dsa-3828
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2669
