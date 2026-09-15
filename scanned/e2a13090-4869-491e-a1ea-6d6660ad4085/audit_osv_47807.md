# [M] CVE-2017-12855

## Summary
Severity: Medium
Advisory: CVE-2017-12855
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2017-08-15
Source: https://osv.dev/vulnerability/CVE-2017-12855
Type: osv

## Details
Xen maintains the _GTF_{read,writ}ing bits as appropriate, to inform the guest that a grant is in use. A guest is expected not to modify the grant details while it is in use, whereas the guest is free to modify/reuse the grant entry when it is not in use. Under some circumstances, Xen will clear the status bits too early, incorrectly informing the guest that the grant is no longer in use. A guest may prematurely believe that a granted frame is safely private again, and reuse it in a way which contains sensitive information, while the domain on the far end of the grant is still using the grant. Xen 4.9, 4.8, 4.7, 4.6, and 4.5 are affected.

## References
- https://support.citrix.com/article/CTX225941
- http://www.debian.org/security/2017/dsa-3969
- http://www.securityfocus.com/bid/100341
- http://www.securitytracker.com/id/1039177
- http://xenbits.xen.org/xsa/advisory-230.html
