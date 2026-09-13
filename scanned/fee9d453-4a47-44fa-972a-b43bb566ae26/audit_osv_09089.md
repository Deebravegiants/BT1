# [M] CVE-2016-7796

## Summary
Severity: Medium
Advisory: CVE-2016-7796
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-10-13
Source: https://osv.dev/vulnerability/CVE-2016-7796
Type: osv

## Details
The manager_dispatch_notify_fd function in systemd allows local users to cause a denial of service (system hang) via a zero-length message received over a notify socket, which causes an error to be returned and the notification handler to be disabled.

## References
- http://www.securitytracker.com/id/1037320
- http://lists.opensuse.org/opensuse-security-announce/2016-10/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2016-10/msg00016.html
- http://rhn.redhat.com/errata/RHSA-2017-0003.html
- http://www.openwall.com/lists/oss-security/2016/09/30/1
- http://www.securityfocus.com/bid/93250
- https://rhn.redhat.com/errata/RHBA-2015-2092.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1381911
- https://github.com/systemd/systemd/issues/4234#issuecomment-250441246
- https://www.agwa.name/blog/post/how_to_crash_systemd_in_one_tweet
