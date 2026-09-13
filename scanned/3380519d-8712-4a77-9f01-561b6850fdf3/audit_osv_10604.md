# [M] CVE-2017-17722

## Summary
Severity: Medium
Advisory: CVE-2017-17722
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-12
Source: https://osv.dev/vulnerability/CVE-2017-17722
Type: osv

## Details
In Exiv2 0.26, there is a reachable assertion in the readHeader function in bigtiffimage.cpp, which will lead to a remote denial of service attack via a crafted TIFF file.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1524116
