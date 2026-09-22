# [C] CVE-2014-8241

## Summary
Severity: Critical
Advisory: CVE-2014-8241
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-14
Source: https://osv.dev/vulnerability/CVE-2014-8241
Type: osv

## Details
XRegion in TigerVNC allows remote VNC servers to cause a denial of service (NULL pointer dereference) by leveraging failure to check a malloc return value, a similar issue to CVE-2014-6052.

## References
- http://www.securityfocus.com/bid/70390
- https://rhn.redhat.com/errata/RHSA-2015-2233.html
- http://seclists.org/oss-sec/2014/q4/278
- http://seclists.org/oss-sec/2014/q4/300
- https://bugzilla.redhat.com/show_bug.cgi?id=1151312
- http://www.oracle.com/technetwork/topics/security/bulletinoct2015-2511968.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinoct2015-2719645.html
