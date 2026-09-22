# [M] CVE-2018-13251

## Summary
Severity: Medium
Advisory: CVE-2018-13251
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-05
Source: https://osv.dev/vulnerability/CVE-2018-13251
Type: osv

## Details
In libming 0.4.8, there is an excessive memory allocation attempt in the readBytes function of the util/read.c file, related to parseSWF_DEFINEBITSJPEG2. Remote attackers could leverage this vulnerability to cause a denial-of-service via a crafted swf file.

## References
- https://github.com/libming/libming/issues/149
