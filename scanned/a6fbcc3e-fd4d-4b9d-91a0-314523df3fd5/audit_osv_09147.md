# [C] CVE-2016-8620

## Summary
Severity: Critical
Advisory: CVE-2016-8620
Aliases: CURL-CVE-2016-8620
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-01
Source: https://osv.dev/vulnerability/CVE-2016-8620
Type: osv

## Details
The 'globbing' feature in curl before version 7.51.0 has a flaw that leads to integer overflow and out-of-bounds read via user controlled input.

## References
- http://www.securityfocus.com/bid/94102
- http://www.securitytracker.com/id/1037192
- https://access.redhat.com/errata/RHSA-2018:3558
- https://curl.haxx.se/docs/adv_20161102F.html
- https://security.gentoo.org/glsa/201701-47
- https://www.tenable.com/security/tns-2016-21
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-8620
