# [M] CVE-2017-14857

## Summary
Severity: Medium
Advisory: CVE-2017-14857
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-29
Source: https://osv.dev/vulnerability/CVE-2017-14857
Type: osv

## Details
In Exiv2 0.26, there is an invalid free in the Image class in image.cpp that leads to a Segmentation fault. A crafted input will lead to a denial of service attack.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1495043
