# [H] CVE-2018-7339

## Summary
Severity: High
Advisory: CVE-2018-7339
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-7339
Type: osv

## Details
The MP4Atom class in mp4atom.cpp in MP4v2 through 2.0.0 mishandles Entry Number validation for the MP4 Table Property, which allows remote attackers to cause a denial of service (overflow, insufficient memory allocation, and segmentation fault) or possibly have unspecified other impact via a crafted mp4 file.

## References
- https://github.com/pingsuewim/libmp4_bof
