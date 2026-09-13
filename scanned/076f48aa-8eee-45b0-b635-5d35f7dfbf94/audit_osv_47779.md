# [H] CVE-2017-12134

## Summary
Severity: High
Advisory: CVE-2017-12134
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-08-24
Source: https://osv.dev/vulnerability/CVE-2017-12134
Type: osv

## Details
The xen_biovec_phys_mergeable function in drivers/xen/biomerge.c in Xen might allow local OS guest users to corrupt block device data streams and consequently obtain sensitive memory information, cause a denial of service, or gain host OS privileges by leveraging incorrect block IO merge-ability calculation.

## References
- https://usn.ubuntu.com/3655-2/
- https://usn.ubuntu.com/3655-1/
- http://www.openwall.com/lists/oss-security/2017/08/15/4
- http://www.securityfocus.com/bid/100343
- https://security.gentoo.org/glsa/201801-14
- http://www.debian.org/security/2017/dsa-3981
- http://www.securitytracker.com/id/1039176
- http://xenbits.xen.org/xsa/advisory-229.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1477656
- https://support.citrix.com/article/CTX225941
