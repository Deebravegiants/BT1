# [H] CVE-2017-12136

## Summary
Severity: High
Advisory: CVE-2017-12136
CVSS: 7.8 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-08-24
Source: https://osv.dev/vulnerability/CVE-2017-12136
Type: osv

## Details
Race condition in the grant table code in Xen 4.6.x through 4.9.x allows local guest OS administrators to cause a denial of service (free list corruption and host crash) or gain privileges on the host via vectors involving maptrack free list handling.

## References
- http://www.debian.org/security/2017/dsa-3969
- http://www.securityfocus.com/bid/100346
- http://www.securitytracker.com/id/1039175
- https://security.gentoo.org/glsa/201801-14
- https://support.citrix.com/article/CTX225941
- http://www.openwall.com/lists/oss-security/2017/08/15/3
- http://xenbits.xen.org/xsa/advisory-228.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1477651
