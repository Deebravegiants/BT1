# [H] CVE-2018-9846

## Summary
Severity: High
Advisory: CVE-2018-9846
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-07
Source: https://osv.dev/vulnerability/CVE-2018-9846
Type: osv

## Details
In Roundcube from versions 1.2.0 to 1.3.5, with the archive plugin enabled and configured, it's possible to exploit the unsanitized, user-controlled "_uid" parameter (in an archive.php _task=mail&_mbox=INBOX&_action=plugin.move2archive request) to perform an MX (IMAP) injection attack by placing an IMAP command after a %0d%0a sequence. NOTE: this is less easily exploitable in 1.3.4 and later because of a Same Origin Policy protection mechanism.

## References
- https://medium.com/%40ndrbasi/cve-2018-9846-roundcube-303097048b0a
- https://www.debian.org/security/2018/dsa-4181
- https://github.com/roundcube/roundcubemail/issues/6229
- https://github.com/roundcube/roundcubemail/issues/6238
