# [H] CVE-2016-0727

## Summary
Severity: High
Advisory: CVE-2016-0727
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/CVE-2016-0727
Type: osv

## Details
The crontab script in the ntp package before 1:4.2.6.p3+dfsg-1ubuntu3.11 on Ubuntu 12.04 LTS, before 1:4.2.6.p5+dfsg-3ubuntu2.14.04.10 on Ubuntu 14.04 LTS, on Ubuntu Wily, and before 1:4.2.8p4+dfsg-3ubuntu5.3 on Ubuntu 16.04 LTS allows local users with access to the ntp account to write to arbitrary files and consequently gain privileges via vectors involving statistics directory cleanup.

## References
- http://www.securityfocus.com/bid/81552
- http://www.securitytracker.com/id/1034808
- http://www.ubuntu.com/usn/USN-3096-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1382369
- https://bugs.launchpad.net/ubuntu/+source/ntp/+bug/1528050
- http://packetstormsecurity.com/files/141913/NTP-Privilege-Escalation.html
