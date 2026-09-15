# [M] CVE-2021-30046

## Summary
Severity: Medium
Advisory: CVE-2021-30046
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-06
Source: https://osv.dev/vulnerability/CVE-2021-30046
Type: osv

## Details
VIGRA Computer Vision Library Version-1-11-1 contains a segmentation fault vulnerability in the impex.hxx read_image_band() function, in which a crafted file can cause a denial of service.

## References
- https://github.com/ukoethe/vigra/issues/494
