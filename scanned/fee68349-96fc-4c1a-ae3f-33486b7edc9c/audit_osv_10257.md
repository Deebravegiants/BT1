# [H] CVE-2017-14629

## Summary
Severity: High
Advisory: CVE-2017-14629
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/CVE-2017-14629
Type: osv

## Details
In sam2p 0.49.3, the in_xpm_reader function in in_xpm.cpp has an integer signedness error, leading to a crash when writing to an out-of-bounds array element.

## References
- https://github.com/pts/sam2p/issues/14
