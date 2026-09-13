# [M] CVE-2007-5626

## Summary
Severity: Medium
Advisory: CVE-2007-5626
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2007-10-23
Source: https://osv.dev/vulnerability/CVE-2007-5626
Type: osv

## Details
make_catalog_backup in Bacula 2.2.5, and probably earlier, sends a MySQL password as a command line argument, and sometimes transmits cleartext e-mail containing this command line, which allows context-dependent attackers to obtain the password by listing the process and its arguments, or by sniffing the network.

## References
- http://bugs.bacula.org/view.php?id=990
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=446809
- http://secunia.com/advisories/27243
- http://secunia.com/advisories/31184
- http://security.gentoo.org/glsa/glsa-200807-10.xml
- http://www.securityfocus.com/bid/26156
- http://www.vupen.com/english/advisories/2007/3572
- https://exchange.xforce.ibmcloud.com/vulnerabilities/37336
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=446809
- http://bugs.bacula.org/view.php?id=990
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=446809
- http://www.vupen.com/english/advisories/2007/3572
- http://osvdb.org/41861
- http://www.securityfocus.com/bid/26156
