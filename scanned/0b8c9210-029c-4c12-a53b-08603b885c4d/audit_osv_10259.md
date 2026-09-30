# [C] CVE-2017-14631

## Summary
Severity: Critical
Advisory: CVE-2017-14631
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/CVE-2017-14631
Type: osv

## Details
In sam2p 0.49.3, the pcxLoadRaster function in in_pcx.cpp has an integer signedness error leading to a heap-based buffer overflow.

## References
- https://github.com/pts/sam2p/issues/14
