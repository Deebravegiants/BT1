# [H] CVE-2018-10847

## Summary
Severity: High
Advisory: CVE-2018-10847
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-30
Source: https://osv.dev/vulnerability/CVE-2018-10847
Type: osv

## Details
prosody before versions 0.10.2, 0.9.14 is vulnerable to an Authentication Bypass. Prosody did not verify that the virtual host associated with a user session remained the same across stream restarts. A user may authenticate to XMPP host A and migrate their authenticated session to XMPP host B of the same Prosody instance.

## References
- https://blog.prosody.im/prosody-0-10-2-security-release/
- https://issues.prosody.im/1147
- https://prosody.im/security/advisory_20180531/
- https://www.debian.org/security/2018/dsa-4216
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10847
