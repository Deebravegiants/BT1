# [H] CVE-2017-8904

## Summary
Severity: High
Advisory: CVE-2017-8904
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-05-11
Source: https://osv.dev/vulnerability/CVE-2017-8904
Type: osv

## Details
Xen through 4.8.x mishandles the "contains segment descriptors" property during GNTTABOP_transfer (aka guest transfer) operations, which might allow PV guest OS users to execute arbitrary code on the host OS, aka XSA-214.

## References
- http://www.securityfocus.com/bid/98428
- http://www.securitytracker.com/id/1038387
- https://blog.xenproject.org/2017/05/02/updates-on-xsa-213-xsa-214-and-xsa-215/
- https://security.gentoo.org/glsa/201705-11
- https://xenbits.xen.org/xsa/advisory-214.html
