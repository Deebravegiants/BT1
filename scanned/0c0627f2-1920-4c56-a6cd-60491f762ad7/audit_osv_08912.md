# [C] CVE-2016-6662

## Summary
Severity: Critical
Advisory: CVE-2016-6662
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-20
Source: https://osv.dev/vulnerability/CVE-2016-6662
Type: osv

## Details
Oracle MySQL through 5.5.52, 5.6.x through 5.6.33, and 5.7.x through 5.7.15; MariaDB before 5.5.51, 10.0.x before 10.0.27, and 10.1.x before 10.1.17; and Percona Server before 5.5.51-38.1, 5.6.x before 5.6.32-78.0, and 5.7.x before 5.7.14-7 allow local users to create arbitrary configurations and bypass certain protection mechanisms by setting general_log_file to a my.cnf configuration. NOTE: this can be leveraged to execute arbitrary code with root privileges by setting malloc_lib. NOTE: the affected MySQL version information is from Oracle's October 2016 CPU. Oracle has not commented on third-party claims that the issue was silently patched in MySQL 5.5.52, 5.6.33, and 5.7.15.

## References
- http://legalhackers.com/advisories/MySQL-Exploit-Remote-Root-Code-Execution-Privesc-CVE-2016-6662.html
- http://rhn.redhat.com/errata/RHSA-2016-2058.html
- http://rhn.redhat.com/errata/RHSA-2016-2059.html
- http://rhn.redhat.com/errata/RHSA-2016-2060.html
- http://rhn.redhat.com/errata/RHSA-2016-2061.html
- http://rhn.redhat.com/errata/RHSA-2016-2062.html
- http://rhn.redhat.com/errata/RHSA-2016-2077.html
- http://rhn.redhat.com/errata/RHSA-2016-2130.html
- http://rhn.redhat.com/errata/RHSA-2016-2131.html
- http://rhn.redhat.com/errata/RHSA-2016-2595.html
- http://rhn.redhat.com/errata/RHSA-2016-2749.html
- http://rhn.redhat.com/errata/RHSA-2016-2927.html
- http://rhn.redhat.com/errata/RHSA-2016-2928.html
- http://rhn.redhat.com/errata/RHSA-2017-0184.html
- http://seclists.org/fulldisclosure/2016/Sep/23
- http://www.debian.org/security/2016/dsa-3666
- http://www.openwall.com/lists/oss-security/2016/09/12/3
- http://www.securityfocus.com/bid/92912
- http://www.securitytracker.com/id/1036769
- https://mariadb.com/kb/en/mariadb/mariadb-10027-release-notes/
