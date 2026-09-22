# [C] CVE-2017-14637

## Summary
Severity: Critical
Advisory: CVE-2017-14637
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-09-22
Source: https://osv.dev/vulnerability/CVE-2017-14637
Type: osv

## Details
In sam2p 0.49.3, there is an invalid read of size 2 in the parse_rgb function in in_xpm.cpp. However, this can also cause a write to an illegal address.

## References
- https://github.com/pts/sam2p/issues/14
