# [M] CVE-2016-4489

## Summary
Severity: Medium
Advisory: CVE-2016-4489
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-24
Source: https://osv.dev/vulnerability/CVE-2016-4489
Type: osv

## Details
Integer overflow in the gnu_special function in libiberty allows remote attackers to cause a denial of service (segmentation fault and crash) via a crafted binary, related to the "demangling of virtual tables."

## References
- http://www.openwall.com/lists/oss-security/2016/05/05/5
- http://www.openwall.com/lists/oss-security/2016/05/05/5
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=70492
- http://www.securityfocus.com/bid/90017
