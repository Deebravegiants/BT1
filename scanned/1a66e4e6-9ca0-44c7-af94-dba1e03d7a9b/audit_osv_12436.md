# [H] CVE-2018-12015

## Summary
Severity: High
Advisory: CVE-2018-12015
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-06-07
Source: https://osv.dev/vulnerability/CVE-2018-12015
Type: osv

## Details
In Perl through 5.26.2, the Archive::Tar module allows remote attackers to bypass a directory-traversal protection mechanism, and overwrite arbitrary files, via an archive file containing a symlink and a regular file with the same name.

## References
- https://www.oracle.com/security-alerts/cpujul2020.html
- http://seclists.org/fulldisclosure/2019/Mar/49
- http://www.securityfocus.com/bid/104423
- http://www.securitytracker.com/id/1041048
- https://access.redhat.com/errata/RHSA-2019:2097
- https://seclists.org/bugtraq/2019/Mar/42
- https://support.apple.com/kb/HT209600
- https://usn.ubuntu.com/3684-1/
- https://usn.ubuntu.com/3684-2/
- https://www.debian.org/security/2018/dsa-4226
- https://security.netapp.com/advisory/ntap-20180927-0001/
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=900834
