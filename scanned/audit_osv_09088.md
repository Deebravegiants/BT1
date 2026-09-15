# [M] CVE-2016-7795

## Summary
Severity: Medium
Advisory: CVE-2016-7795
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-10-13
Source: https://osv.dev/vulnerability/CVE-2016-7795
Type: osv

## Details
The manager_invoke_notify_message function in systemd 231 and earlier allows local users to cause a denial of service (assertion failure and PID 1 hang) via a zero-length message received over a notify socket.

## References
- http://www.securitytracker.com/id/1037320
- http://rhn.redhat.com/errata/RHSA-2016-2610.html
- http://rhn.redhat.com/errata/RHSA-2016-2694.html
- http://www.openwall.com/lists/oss-security/2016/09/28/9
- http://www.openwall.com/lists/oss-security/2016/09/30/1
- http://www.securityfocus.com/bid/93223
- http://www.ubuntu.com/usn/USN-3094-1
- https://github.com/systemd/systemd/issues/4234
- https://www.agwa.name/blog/post/how_to_crash_systemd_in_one_tweet
