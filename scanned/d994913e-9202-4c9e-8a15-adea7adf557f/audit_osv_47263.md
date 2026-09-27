# [M] CVE-2016-1967

## Summary
Severity: Medium
Advisory: CVE-2016-1967
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2016-03-13
Source: https://osv.dev/vulnerability/CVE-2016-1967
Type: osv

## Details
Mozilla Firefox before 45.0 does not properly restrict the availability of IFRAME Resource Timing API times, which allows remote attackers to bypass the Same Origin Policy and obtain sensitive information via crafted JavaScript code that leverages history.back and performance.getEntries calls after restoring a browser session. NOTE: this vulnerability exists because of an incomplete fix for CVE-2015-7207.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00029.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00031.html
- http://www.securitytracker.com/id/1035215
- http://www.mozilla.org/security/announce/2016/mfsa2016-29.html
- http://www.ubuntu.com/usn/USN-2917-1
- http://www.ubuntu.com/usn/USN-2917-2
- http://www.ubuntu.com/usn/USN-2917-3
- https://security.gentoo.org/glsa/201605-06
- https://bugzilla.mozilla.org/show_bug.cgi?id=1246956
