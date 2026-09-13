# [C] CVE-2014-9984

## Summary
Severity: Critical
Advisory: CVE-2014-9984
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-12
Source: https://osv.dev/vulnerability/CVE-2014-9984
Type: osv

## Details
nscd in the GNU C Library (aka glibc or libc6) before version 2.20 does not correctly compute the size of an internal buffer when processing netgroup requests, possibly leading to an nscd daemon crash or code execution as the user running nscd.

## References
- https://sourceware.org/bugzilla/show_bug.cgi?id=16695
- https://sourceware.org/bugzilla/show_bug.cgi?id=16695
- https://sourceware.org/bugzilla/show_bug.cgi?id=16695
- http://packetstormsecurity.com/files/153278/WAGO-852-Industrial-Managed-Switch-Series-Code-Execution-Hardcoded-Credentials.html
- http://packetstormsecurity.com/files/154361/Cisco-Device-Hardcoded-Credentials-GNU-glibc-BusyBox.html
- http://seclists.org/fulldisclosure/2019/Jun/18
- http://seclists.org/fulldisclosure/2019/Sep/7
- http://www.securityfocus.com/bid/99071
- https://seclists.org/bugtraq/2019/Jun/14
- https://seclists.org/bugtraq/2019/Sep/7
- https://sourceware.org/git/gitweb.cgi?p=glibc.git%3Ba=commit%3Bh=c44496df2f090a56d3bf75df930592dac6bba46f
