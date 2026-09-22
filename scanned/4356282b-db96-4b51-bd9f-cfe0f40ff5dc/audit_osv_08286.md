# [H] CVE-2016-2119

## Summary
Severity: High
Advisory: CVE-2016-2119
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-07-07
Source: https://osv.dev/vulnerability/CVE-2016-2119
Type: osv

## Details
libcli/smb/smbXcli_base.c in Samba 4.x before 4.2.14, 4.3.x before 4.3.11, and 4.4.x before 4.4.5 allows man-in-the-middle attackers to bypass a client-signing protection mechanism, and consequently spoof SMB2 and SMB3 servers, via the (1) SMB2_SESSION_FLAG_IS_GUEST or (2) SMB2_SESSION_FLAG_IS_NULL flag.

## References
- http://lists.opensuse.org/opensuse-updates/2016-07/msg00060.html
- http://rhn.redhat.com/errata/RHSA-2016-1486.html
- http://rhn.redhat.com/errata/RHSA-2016-1487.html
- http://rhn.redhat.com/errata/RHSA-2016-1494.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.securityfocus.com/bid/91700
- http://www.securitytracker.com/id/1036244
- https://security.gentoo.org/glsa/201805-07
- https://www.samba.org/samba/security/CVE-2016-2119.html
