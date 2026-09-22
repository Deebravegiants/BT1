# [H] CVE-2020-29040

## Summary
Severity: High
Advisory: CVE-2020-29040
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-11-24
Source: https://osv.dev/vulnerability/CVE-2020-29040
Type: osv

## Details
An issue was discovered in Xen through 4.14.x allowing x86 HVM guest OS users to cause a denial of service (stack corruption), cause a data leak, or possibly gain privileges because of an off-by-one error. NOTE: this issue is caused by an incorrect fix for CVE-2020-27671.

## References
- http://www.openwall.com/lists/oss-security/2021/01/19/4
- http://xenbits.xen.org/xsa/advisory-355.html
- https://xenbits.xen.org/xsa/advisory-355.html
