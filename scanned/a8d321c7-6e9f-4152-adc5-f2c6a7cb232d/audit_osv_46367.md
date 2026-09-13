# [M] CVE-2006-1058

## Summary
Severity: Medium
Advisory: CVE-2006-1058
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2006-04-04
Source: https://osv.dev/vulnerability/CVE-2006-1058
Type: osv

## Details
BusyBox 1.1.1 does not use a salt when generating passwords, which makes it easier for local users to guess passwords from a stolen password file using techniques such as rainbow tables.

## References
- http://secunia.com/advisories/19477
- http://secunia.com/advisories/25098
- http://secunia.com/advisories/25848
- http://support.avaya.com/elmodocs2/security/ASA-2007-250.htm
- http://www.securityfocus.com/bid/17330
- https://exchange.xforce.ibmcloud.com/vulnerabilities/25569
- http://bugs.busybox.net/view.php?id=604
- http://www.redhat.com/support/errata/RHSA-2007-0244.html
- http://www.securityfocus.com/bid/17330
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A9483
