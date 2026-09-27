# [H] CVE-2017-7228

## Summary
Severity: High
Advisory: CVE-2017-7228
CVSS: 8.2 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-04-04
Source: https://osv.dev/vulnerability/CVE-2017-7228
Type: osv

## Details
An issue (known as XSA-212) was discovered in Xen, with fixes available for 4.8.x, 4.7.x, 4.6.x, 4.5.x, and 4.4.x. The earlier XSA-29 fix introduced an insufficient check on XENMEM_exchange input, allowing the caller to drive hypervisor memory accesses outside of the guest provided input/output arrays.

## References
- http://openwall.com/lists/oss-security/2017/04/04/3
- http://www.debian.org/security/2017/dsa-3847
- http://www.securityfocus.com/bid/97375
- http://xenbits.xen.org/xsa/advisory-212.html
- https://googleprojectzero.blogspot.com/2017/04/pandavirtualization-exploiting-xen.html
- http://openwall.com/lists/oss-security/2017/04/04/3
- https://googleprojectzero.blogspot.com/2017/04/pandavirtualization-exploiting-xen.html
- http://xenbits.xen.org/xsa/advisory-212.html
- http://www.securitytracker.com/id/1038223
- https://github.com/QubesOS/qubes-secpack/blob/master/QSBs/qsb-029-2017.txt
- https://www.exploit-db.com/exploits/41870/
