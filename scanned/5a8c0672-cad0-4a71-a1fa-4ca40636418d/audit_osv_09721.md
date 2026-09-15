# [H] CVE-2017-11103

## Summary
Severity: High
Advisory: CVE-2017-11103
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-13
Source: https://osv.dev/vulnerability/CVE-2017-11103
Type: osv

## Details
Heimdal before 7.4 allows remote attackers to impersonate services with Orpheus' Lyre attacks because it obtains service-principal names in a way that violates the Kerberos 5 protocol specification. In _krb5_extract_ticket() the KDC-REP service name must be obtained from the encrypted version stored in 'enc_part' instead of the unencrypted version stored in 'ticket'. Use of the unencrypted version provides an opportunity for successful server impersonation and other attacks. NOTE: this CVE is only for Heimdal and other products that embed Heimdal code; it does not apply to other instances in which this part of the Kerberos 5 protocol specification is violated.

## References
- http://www.debian.org/security/2017/dsa-3912
- http://www.h5l.org/advisories.html?show=2017-07-11
- http://www.securityfocus.com/bid/99551
- http://www.securitytracker.com/id/1038876
- http://www.securitytracker.com/id/1039427
- https://github.com/heimdal/heimdal/releases/tag/heimdal-7.4.0
- https://support.apple.com/HT208112
- https://support.apple.com/HT208144
- https://support.apple.com/HT208221
- https://www.freebsd.org/security/advisories/FreeBSD-SA-17:05.heimdal.asc
- https://www.orpheus-lyre.info/
- https://www.samba.org/samba/security/CVE-2017-11103.html
