# [C] CVE-2017-14630

## Summary
Severity: Critical
Advisory: CVE-2017-14630
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/CVE-2017-14630
Type: osv

## Details
In sam2p 0.49.3, an integer overflow exists in the pcxLoadImage24 function of the file in_pcx.cpp, leading to an invalid write operation.

## References
- https://github.com/pts/sam2p/issues/14
