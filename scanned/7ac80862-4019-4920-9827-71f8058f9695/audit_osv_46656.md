# [C] CVE-2014-7169

## Summary
Severity: Critical
Advisory: CVE-2014-7169
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2014-09-25
Source: https://osv.dev/vulnerability/CVE-2014-7169
Type: osv

## Details
GNU Bash through 4.3 bash43-025 processes trailing strings after certain malformed function definitions in the values of environment variables, which allows remote attackers to write to files or possibly have unknown other impact via a crafted environment, as demonstrated by vectors involving the ForceCommand feature in OpenSSH sshd, the mod_cgi and mod_cgid modules in the Apache HTTP Server, scripts executed by unspecified DHCP clients, and other situations in which setting the environment occurs across a privilege boundary from Bash execution.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2014-6271.

## References
- http://advisories.mageia.org/MGASA-2014-0393.html
- http://jvn.jp/en/jp/JVN55667175/index.html
- http://jvndb.jvn.jp/jvndb/JVNDB-2014-000126
- http://lcamtuf.blogspot.com/2014/09/quick-notes-about-bash-bug-its-impact.html
- http://linux.oracle.com/errata/ELSA-2014-1306.html
- http://linux.oracle.com/errata/ELSA-2014-3075.html
- http://linux.oracle.com/errata/ELSA-2014-3077.html
- http://linux.oracle.com/errata/ELSA-2014-3078.html
- http://lists.opensuse.org/opensuse-security-announce/2014-09/msg00038.html
- http://lists.opensuse.org/opensuse-security-announce/2014-09/msg00041.html
- http://lists.opensuse.org/opensuse-security-announce/2014-09/msg00042.html
- http://lists.opensuse.org/opensuse-security-announce/2014-09/msg00044.html
- http://lists.opensuse.org/opensuse-security-announce/2014-09/msg00048.html
- http://lists.opensuse.org/opensuse-security-announce/2014-10/msg00004.html
- http://lists.opensuse.org/opensuse-updates/2014-10/msg00023.html
- http://lists.opensuse.org/opensuse-updates/2014-10/msg00025.html
- http://packetstormsecurity.com/files/128517/VMware-Security-Advisory-2014-0010.html
- http://packetstormsecurity.com/files/128567/CA-Technologies-GNU-Bash-Shellshock.html
- http://rhn.redhat.com/errata/RHSA-2014-1306.html
- http://rhn.redhat.com/errata/RHSA-2014-1311.html
