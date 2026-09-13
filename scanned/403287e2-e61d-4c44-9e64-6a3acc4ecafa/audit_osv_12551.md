# [C] CVE-2018-12882

## Summary
Severity: Critical
Advisory: CVE-2018-12882
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-26
Source: https://osv.dev/vulnerability/CVE-2018-12882
Type: osv

## Details
exif_read_from_impl in ext/exif/exif.c in PHP 7.2.x through 7.2.7 allows attackers to trigger a use-after-free (in exif_read_from_file) because it closes a stream that it is not responsible for closing. The vulnerable code is reachable through the PHP exif_read_data function.

## References
- http://www.securityfocus.com/bid/104551
- https://security.netapp.com/advisory/ntap-20181109-0001/
- https://usn.ubuntu.com/3702-1/
- https://usn.ubuntu.com/3702-2/
- https://bugs.php.net/bug.php?id=76409
