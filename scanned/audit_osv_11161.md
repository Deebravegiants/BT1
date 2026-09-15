# [M] CVE-2017-6437

## Summary
Severity: Medium
Advisory: CVE-2017-6437
CVSS: 5.0 (CVSS:3.0/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-6437
Type: osv

## Details
The base64encode function in base64.c in libimobiledevice libplist 1.12 allows local users to cause a denial of service (out-of-bounds read) via a crafted plist file.

## References
- http://www.securityfocus.com/bid/97291
- https://github.com/libimobiledevice/libplist/issues/100
