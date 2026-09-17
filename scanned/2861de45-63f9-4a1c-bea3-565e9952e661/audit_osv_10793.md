# [H] CVE-2017-2665

## Summary
Severity: High
Advisory: CVE-2017-2665
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-06
Source: https://osv.dev/vulnerability/CVE-2017-2665
Type: osv

## Details
The skyring-setup command creates random password for mongodb skyring database but it writes password in plain text to /etc/skyring/skyring.conf file which is owned by root but read by local user. Any local user who has access to system running skyring service will be able to get password in plain text.

## References
- http://www.securityfocus.com/bid/97612
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2665
