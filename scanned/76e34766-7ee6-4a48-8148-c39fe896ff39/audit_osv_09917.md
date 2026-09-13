# [M] CVE-2017-12144

## Summary
Severity: Medium
Advisory: CVE-2017-12144
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-02
Source: https://osv.dev/vulnerability/CVE-2017-12144
Type: osv

## Details
In ytnef 1.9.2, an allocation failure was found in the function TNEFFillMapi in ytnef.c, which allows attackers to cause a denial of service via a crafted file.

## References
- http://www.securityfocus.com/bid/100098
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LFJWMUEUC4ILH2HEOCYVVLQT654ZMCGQ/
- https://somevulnsofadlab.blogspot.com/2017/07/ytnefallocation-failed-in-tneffillmapi.html
- https://github.com/Yeraze/ytnef/issues/51
