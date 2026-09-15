# [M] CVE-2022-2719

## Summary
Severity: Medium
Advisory: CVE-2022-2719
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-08-09
Source: https://osv.dev/vulnerability/CVE-2022-2719
Type: osv

## Details
In ImageMagick, a crafted file could trigger an assertion failure when a call to WriteImages was made in MagickWand/operation.c, due to a NULL image list. This could potentially cause a denial of service. This was fixed in upstream ImageMagick version 7.1.0-30.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2719.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-2719
- https://bugzilla.redhat.com/show_bug.cgi?id=2116537
