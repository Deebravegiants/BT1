# [M] CVE-2016-7154

## Summary
Severity: Medium
Advisory: CVE-2016-7154
CVSS: 6.7 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/CVE-2016-7154
Type: osv

## Details
Use-after-free vulnerability in the FIFO event channel code in Xen 4.4.x allows local guest OS administrators to cause a denial of service (host crash) and possibly execute arbitrary code or obtain sensitive information via an invalid guest frame number.

## References
- http://www.c7zero.info/stuff/csw2017_ExploringYourSystemDeeper_updated.pdf
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
- http://www.debian.org/security/2016/dsa-3663
- http://www.securityfocus.com/bid/92863
- http://www.securitytracker.com/id/1036754
- http://support.citrix.com/article/CTX216071
- http://xenbits.xen.org/xsa/advisory-188.html
- http://xenbits.xen.org/xsa/xsa188.patch
