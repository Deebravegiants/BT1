# [M] CVE-2017-6512

## Summary
Severity: Medium
Advisory: CVE-2017-6512
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-06-01
Source: https://osv.dev/vulnerability/CVE-2017-6512
Type: osv

## Details
Race condition in the rmtree and remove_tree functions in the File-Path module before 2.13 for Perl allows attackers to set the mode on arbitrary files via vectors involving directory-permission loosening logic.

## References
- http://security.cucumberlinux.com/security/details.php?id=153
- http://www.securityfocus.com/bid/99180
- http://www.securitytracker.com/id/1038610
- https://security.gentoo.org/glsa/201709-12
- https://usn.ubuntu.com/3625-2/
- http://cpansearch.perl.org/src/JKEENAN/File-Path-2.13/Changes
- http://www.debian.org/security/2017/dsa-3873
- https://usn.ubuntu.com/3625-1/
- https://rt.cpan.org/Ticket/Display.html?id=121951
