# [M] CVE-2017-16661

## Summary
Severity: Medium
Advisory: CVE-2017-16661
CVSS: 4.9 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-11-08
Source: https://osv.dev/vulnerability/CVE-2017-16661
Type: osv

## Details
Cacti 1.1.27 allows remote authenticated administrators to read arbitrary files by placing the Log Path into a private directory, and then making a clog.php?filename= request, as demonstrated by filename=passwd (with a Log Path under /etc) to read /etc/passwd.

## References
- https://github.com/Cacti/cacti/issues/1066
