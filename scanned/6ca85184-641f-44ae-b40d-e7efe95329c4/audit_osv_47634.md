# [M] CVE-2016-9646

## Summary
Severity: Medium
Advisory: CVE-2016-9646
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2018-04-13
Source: https://osv.dev/vulnerability/CVE-2016-9646
Type: osv

## Details
ikiwiki before 3.20161229 incorrectly called the CGI::FormBuilder->field method (similar to the CGI->param API that led to Bugzilla's CVE-2014-1572), which can be abused to lead to commit metadata forgery.

## References
- https://ikiwiki.info/security/#cve-2016-9646
- https://marc.info/?l=oss-security&m=148304341511854&w=2
- https://www.debian.org/security/2017/dsa-3760
- https://security-tracker.debian.org/tracker/CVE-2016-9646
