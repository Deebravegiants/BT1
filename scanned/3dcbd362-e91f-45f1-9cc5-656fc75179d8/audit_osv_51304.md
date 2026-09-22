# [M] CVE-2021-28275

## Summary
Severity: Medium
Advisory: CVE-2021-28275
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-03-23
Source: https://osv.dev/vulnerability/CVE-2021-28275
Type: osv

## Details
A Denial of Service vulnerability exists in jhead 3.04 and 3.05 due to a wild address read in the Get16u function in exif.c in will cause segmentation fault via a crafted_file.

## References
- https://security.gentoo.org/glsa/202210-17
- https://github.com/Matthias-Wandel/jhead/issues/17
