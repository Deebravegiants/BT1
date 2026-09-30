# [C] CVE-2014-6271

## Summary
Severity: Critical
Advisory: CVE-2014-6271
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2014-09-24
Source: https://osv.dev/vulnerability/CVE-2014-6271
Type: osv

## Details
GNU Bash through 4.3 processes trailing strings after function definitions in the values of environment variables, which allows remote attackers to execute arbitrary code via a crafted environment, as demonstrated by vectors involving the ForceCommand feature in OpenSSH sshd, the mod_cgi and mod_cgid modules in the Apache HTTP Server, scripts executed by unspecified DHCP clients, and other situations in which setting the environment occurs across a privilege boundary from Bash execution, aka "ShellShock."  NOTE: the original fix for this issue was incorrect; CVE-2014-7169 has been assigned to cover the vulnerability that is still present after the incorrect fix.

## References
- http://advisories.mageia.org/MGASA-2014-0388.html
- http://archives.neohapsis.com/archives/bugtraq/2014-10/0101.html
- http://jvn.jp/en/jp/JVN55667175/index.html
- http://jvndb.jvn.jp/jvndb/JVNDB-2014-000126
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10673
- http://lcamtuf.blogspot.com/2014/09/quick-notes-about-bash-bug-its-impact.html
- http://linux.oracle.com/errata/ELSA-2014-1293.html
- http://linux.oracle.com/errata/ELSA-2014-1294.html
- http://lists.opensuse.org/opensuse-security-announce/2014-09/msg00028.html
- http://lists.opensuse.org/opensuse-security-announce/2014-09/msg00029.html
- http://lists.opensuse.org/opensuse-security-announce/2014-09/msg00034.html
- http://lists.opensuse.org/opensuse-security-announce/2014-09/msg00037.html
- http://lists.opensuse.org/opensuse-security-announce/2014-09/msg00040.html
- http://lists.opensuse.org/opensuse-security-announce/2014-09/msg00044.html
- http://lists.opensuse.org/opensuse-security-announce/2014-09/msg00049.html
- http://lists.opensuse.org/opensuse-security-announce/2014-10/msg00004.html
- http://lists.opensuse.org/opensuse-updates/2014-10/msg00023.html
- http://lists.opensuse.org/opensuse-updates/2014-10/msg00025.html
- http://marc.info/?l=bugtraq&m=141216207813411&w=2
- http://marc.info/?l=bugtraq&m=141216668515282&w=2
