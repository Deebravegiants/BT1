# [M] CVE-2016-9385

## Summary
Severity: Medium
Advisory: CVE-2016-9385
CVSS: 6.0 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-01-23
Source: https://osv.dev/vulnerability/CVE-2016-9385
Type: osv

## Details
The x86 segment base write emulation functionality in Xen 4.4.x through 4.7.x allows local x86 PV guest OS administrators to cause a denial of service (host crash) by leveraging lack of canonical address checks.

## References
- http://www.securityfocus.com/bid/94472
- http://www.securitytracker.com/id/1037342
- https://security.gentoo.org/glsa/201612-56
- http://xenbits.xen.org/xsa/advisory-193.html
- https://support.citrix.com/article/CTX218775
