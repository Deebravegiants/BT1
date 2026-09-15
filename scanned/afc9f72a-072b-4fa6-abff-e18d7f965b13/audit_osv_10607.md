# [M] CVE-2017-17725

## Summary
Severity: Medium
Advisory: CVE-2017-17725
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-12
Source: https://osv.dev/vulnerability/CVE-2017-17725
Type: osv

## Details
In Exiv2 0.26, there is an integer overflow leading to a heap-based buffer over-read in the Exiv2::getULong function in types.cpp. Remote attackers can exploit the vulnerability to cause a denial of service via a crafted image file. Note that this vulnerability is different from CVE-2017-14864, which is an invalid memory address dereference.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1525055
- https://github.com/Exiv2/exiv2/issues/188
