# [C] CVE-2013-7455

## Summary
Severity: Critical
Advisory: CVE-2013-7455
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-07
Source: https://osv.dev/vulnerability/CVE-2013-7455
Type: osv

## Details
Double free vulnerability in the DefaultICCintents function in cmscnvrt.c in liblcms2 in Little CMS 2.x before 2.6 allows remote attackers to execute arbitrary code via a malformed ICC profile that triggers an error in the default intent handler.

## References
- http://www.kb.cert.org/vuls/id/369800
- http://www.ubuntu.com/usn/USN-2961-1
- https://github.com/mm2/Little-CMS/commit/fefaaa43c382eee632ea3ad0cfa915335140e1db
- http://www.kb.cert.org/vuls/id/369800
- https://penteston.com/OSVDB-105462
