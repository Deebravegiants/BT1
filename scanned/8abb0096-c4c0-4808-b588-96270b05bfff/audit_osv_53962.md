# [H] CVE-2023-34319

## Summary
Severity: High
Advisory: CVE-2023-34319
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-09-22
Source: https://osv.dev/vulnerability/CVE-2023-34319
Type: osv

## Details
The fix for XSA-423 added logic to Linux'es netback driver to deal with
a frontend splitting a packet in a way such that not all of the headers
would come in one piece.  Unfortunately the logic introduced there
didn't account for the extreme case of the entire packet being split
into as many pieces as permitted by the protocol, yet still being
smaller than the area that's specially dealt with to keep all (possible)
headers together.  Such an unusual packet would therefore trigger a
buffer overrun in the driver.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- http://packetstormsecurity.com/files/175963/Kernel-Live-Patch-Security-Notice-LSN-0099-1.html
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://security.netapp.com/advisory/ntap-20240202-0001/
- http://xenbits.xen.org/xsa/advisory-432.html
- https://xenbits.xenproject.org/xsa/advisory-432.html
