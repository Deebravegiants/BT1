# [M] CVE-2019-1010004

## Summary
Severity: Medium
Advisory: CVE-2019-1010004
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-15
Source: https://osv.dev/vulnerability/CVE-2019-1010004
Type: osv

## Details
SoX - Sound eXchange 14.4.2 and earlier is affected by: Out-of-bounds Read. The impact is: Denial of Service. The component is: read_samples function at xa.c:219. The attack vector is: Victim must open specially crafted .xa file. NOTE: this may overlap CVE-2017-18189.

## References
- https://sourceforge.net/p/sox/code/ci/master/tree/src/xa.c#l219
- https://sourceforge.net/p/sox/bugs/299/
