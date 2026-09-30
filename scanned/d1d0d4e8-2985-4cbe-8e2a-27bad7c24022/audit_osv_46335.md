# [M] CVE-2001-1494

## Summary
Severity: Medium
Advisory: CVE-2001-1494
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2001-12-31
Source: https://osv.dev/vulnerability/CVE-2001-1494
Type: osv

## Details
script command in the util-linux package before 2.11n allows local users to overwrite arbitrary files by setting a hardlink from the typescript log file to any file on the system, then having root execute the script command.

## References
- http://seclists.org/bugtraq/2001/Dec/0122.html
- http://seclists.org/bugtraq/2001/Dec/0123.html
- http://secunia.com/advisories/16785
- http://secunia.com/advisories/18502
- http://support.avaya.com/elmodocs2/security/ASA-2006-014.htm
- http://www.redhat.com/support/errata/RHSA-2005-782.html
- http://www.securityfocus.com/bid/16280
- https://exchange.xforce.ibmcloud.com/vulnerabilities/7718
- http://seclists.org/bugtraq/2001/Dec/0122.html
- http://seclists.org/bugtraq/2001/Dec/0123.html
- http://www.redhat.com/support/errata/RHSA-2005-782.html
- http://www.securityfocus.com/bid/16280
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A10723
