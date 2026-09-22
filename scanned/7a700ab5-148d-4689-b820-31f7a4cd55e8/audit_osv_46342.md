# [H] CVE-2002-1850

## Summary
Severity: High
Advisory: CVE-2002-1850
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2002-12-31
Source: https://osv.dev/vulnerability/CVE-2002-1850
Type: osv

## Details
mod_cgi in Apache 2.0.39 and 2.0.40 allows local users and possibly remote attackers to cause a denial of service (hang and memory consumption) by causing a CGI script to send a large amount of data to stderr, which results in a read/write deadlock between httpd and the CGI script.

## References
- http://seclists.org/bugtraq/2002/Sep/0253.html
- http://securitytracker.com/id?1007823
- http://www.securityfocus.com/bid/5787
- http://www.securityfocus.com/bid/8725
- http://marc.info/?l=apache-httpd-dev&m=103291952019514&w=2
- http://seclists.org/bugtraq/2002/Sep/0253.html
- http://seclists.org/bugtraq/2002/Sep/0253.html
- http://www.securityfocus.com/bid/5787
- http://issues.apache.org/bugzilla/show_bug.cgi?id=22030
- http://securitytracker.com/id?1007823
- http://www.iss.net/security_center/static/10200.php
- http://www.securityfocus.com/bid/8725
- http://issues.apache.org/bugzilla/show_bug.cgi?id=10515
- http://issues.apache.org/bugzilla/show_bug.cgi?id=22030
- http://cvs.apache.org/viewcvs.cgi/httpd-2.0/modules/generators/mod_cgi.c?r1=1.148.2.7&r2=1.148.2.8
- http://securitytracker.com/id?1007823
- http://www.iss.net/security_center/static/10200.php
- http://www.securityfocus.com/bid/5787
- http://www.securityfocus.com/bid/8725
