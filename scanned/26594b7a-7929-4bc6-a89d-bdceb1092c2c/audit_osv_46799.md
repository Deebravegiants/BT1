# [M] CVE-2015-3243

## Summary
Severity: Medium
Advisory: CVE-2015-3243
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-07-25
Source: https://osv.dev/vulnerability/CVE-2015-3243
Type: osv

## Details
rsyslog uses weak permissions for generating log files, which allows local users to obtain sensitive information by reading files in /var/log/cron.

## References
- http://www.openwall.com/lists/oss-security/2015/06/18/12
- http://www.openwall.com/lists/oss-security/2015/06/20/3
- http://www.securityfocus.com/bid/75298
- http://www.securitytracker.com/id/1032885
- https://bugzilla.redhat.com/show_bug.cgi?id=1232826
- http://www.openwall.com/lists/oss-security/2015/06/18/12
- http://www.openwall.com/lists/oss-security/2015/06/20/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1232826
