# [M] CVE-2017-6197

## Summary
Severity: Medium
Advisory: CVE-2017-6197
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-24
Source: https://osv.dev/vulnerability/CVE-2017-6197
Type: osv

## Details
The r_read_* functions in libr/include/r_endian.h in radare2 1.2.1 allow remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted binary file, as demonstrated by the r_read_le32 function.

## References
- http://www.securityfocus.com/bid/96433
- https://github.com/radare/radare2/commit/1ea23bd6040441a21fbcfba69dce9a01af03f989
- https://github.com/radare/radare2/issues/6816
