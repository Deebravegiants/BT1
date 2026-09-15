# [H] CVE-2016-9928

## Summary
Severity: High
Advisory: CVE-2016-9928
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-02-06
Source: https://osv.dev/vulnerability/CVE-2016-9928
Type: osv

## Details
MCabber before 1.0.4 is vulnerable to roster push attacks, which allows remote attackers to intercept communications, or add themselves as an entity on a 3rd party's roster as another user, which will also garner associated privileges, via crafted XMPP packets.

## References
- http://www.openwall.com/lists/oss-security/2016/12/11/2
- http://www.openwall.com/lists/oss-security/2017/02/09/29
- http://www.securityfocus.com/bid/94862
- https://gultsch.de/gajim_roster_push_and_message_interception.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00031.html
- http://lists.opensuse.org/opensuse-updates/2017-01/msg00130.html
- https://usn.ubuntu.com/4506-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=1403790
- https://bitbucket.org/McKael/mcabber-crew/commits/6e1ead98930d7dd0a520ad17c720ae4908429033/raw
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=845258
