# [C] CVE-2010-3438

## Summary
Severity: Critical
Advisory: CVE-2010-3438
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-12
Source: https://osv.dev/vulnerability/CVE-2010-3438
Type: osv

## Details
libpoe-component-irc-perl before v6.32 does not remove carriage returns and line feeds. This can be used to execute arbitrary IRC commands by passing an argument such as "some text\rQUIT" to the 'privmsg' handler, which would cause the client to disconnect from the server.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=581194
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2010-3438
- https://security-tracker.debian.org/tracker/CVE-2010-3438
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=581194
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=581194
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2010-3438
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2010-3438
