# [M] CVE-2021-31855

## Summary
Severity: Medium
Advisory: CVE-2021-31855
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/CVE-2021-31855
Type: osv

## Details
KDE Messagelib through 5.17.0 reveals cleartext of encrypted messages in some situations. Deleting an attachment of a decrypted encrypted message stored on a remote server (e.g., an IMAP server) causes KMail to upload the decrypted content of the message to the remote server. With a crafted message, a user could be tricked into decrypting an encrypted message and then deleting an attachment attached to this message. If the attacker has access to the messages stored on the email server, then the attacker could read the decrypted content of the encrypted message. This occurs in ViewerPrivate::deleteAttachment in messageviewer/src/viewer/viewer_p.cpp.

## References
- https://kde.org/info/security/advisory-20210429-1.txt
- https://github.com/KDE/messagelib/commit/3b5b171e91ce78b966c98b1292a1bcbc8d984799
