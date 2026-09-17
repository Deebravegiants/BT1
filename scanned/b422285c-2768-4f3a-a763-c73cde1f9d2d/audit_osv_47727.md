# [C] CVE-2017-10917

## Summary
Severity: Critical
Advisory: CVE-2017-10917
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-07-05
Source: https://osv.dev/vulnerability/CVE-2017-10917
Type: osv

## Details
Xen through 4.8.x does not validate the port numbers of polled event channel ports, which allows guest OS users to cause a denial of service (NULL pointer dereference and host OS crash) or possibly obtain sensitive information, aka XSA-221.

## References
- http://www.securityfocus.com/bid/99157
- http://www.securitytracker.com/id/1038731
- http://www.debian.org/security/2017/dsa-3969
- https://security.gentoo.org/glsa/201708-03
- https://xenbits.xen.org/xsa/advisory-221.html
