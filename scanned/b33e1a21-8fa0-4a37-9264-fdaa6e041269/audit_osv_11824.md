# [H] CVE-2017-9953

## Summary
Severity: High
Advisory: CVE-2017-9953
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-26
Source: https://osv.dev/vulnerability/CVE-2017-9953
Type: osv

## Details
There is an invalid free in Image::printIFDStructure that leads to a Segmentation fault in Exiv2 0.26. A crafted input will lead to a remote denial of service attack.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1465061
