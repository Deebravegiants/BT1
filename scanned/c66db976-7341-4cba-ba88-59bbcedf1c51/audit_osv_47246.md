# [H] CVE-2016-1949

## Summary
Severity: High
Advisory: CVE-2016-1949
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-02-13
Source: https://osv.dev/vulnerability/CVE-2016-1949
Type: osv

## Details
Mozilla Firefox before 44.0.2 does not properly restrict the interaction between Service Workers and plugins, which allows remote attackers to bypass the Same Origin Policy via a crafted web site that triggers spoofed responses to requests that use NPAPI, as demonstrated by a request for a crossdomain.xml file.

## References
- http://www.securitytracker.com/id/1035007
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00102.html
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00142.html
- http://www.ubuntu.com/usn/USN-2893-1
- https://security.gentoo.org/glsa/201605-06
- http://www.mozilla.org/security/announce/2016/mfsa2016-13.html
- https://bugzilla.mozilla.org/show_bug.cgi?id=1245724
