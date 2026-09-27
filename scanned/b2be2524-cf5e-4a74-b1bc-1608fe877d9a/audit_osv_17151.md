# [H] CVE-2020-13111

## Summary
Severity: High
Advisory: CVE-2020-13111
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-16
Source: https://osv.dev/vulnerability/CVE-2020-13111
Type: osv

## Details
NaviServer 4.99.4 to 4.99.19 allows denial of service due to the nsd/driver.c ChunkedDecode function not properly validating the length of a chunk. A remote attacker can craft a chunked-transfer request that will result in a negative value being passed to memmove via the size parameter, causing the process to crash.

## References
- https://sourceforge.net/p/naviserver/bugs/89/
- https://bitbucket.org/naviserver/naviserver/commits/a5c3079f1d8996d5f34c9384a440acf3519ca3bb
