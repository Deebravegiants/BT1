# [H] CVE-2016-9383

## Summary
Severity: High
Advisory: CVE-2016-9383
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-01-23
Source: https://osv.dev/vulnerability/CVE-2016-9383
Type: osv

## Details
Xen, when running on a 64-bit hypervisor, allows local x86 guest OS users to modify arbitrary memory and consequently obtain sensitive information, cause a denial of service (host crash), or execute arbitrary code on the host by leveraging broken emulation of bit test instructions.

## References
- http://www.securityfocus.com/bid/94474
- http://www.securitytracker.com/id/1037346
- https://security.gentoo.org/glsa/201612-56
- http://xenbits.xen.org/xsa/advisory-195.html
- https://support.citrix.com/article/CTX218775
