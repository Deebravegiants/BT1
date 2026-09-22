# [H] CVE-2018-1999011

## Summary
Severity: High
Advisory: CVE-2018-1999011
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-07-23
Source: https://osv.dev/vulnerability/CVE-2018-1999011
Type: osv

## Details
FFmpeg before commit 2b46ebdbff1d8dec7a3d8ea280a612b91a582869 contains a Buffer Overflow vulnerability in asf_o format demuxer that can result in heap-buffer-overflow that may result in remote code execution. This attack appears to be exploitable via specially crafted ASF file that has to be provided as input to FFmpeg. This vulnerability appears to have been fixed in 2b46ebdbff1d8dec7a3d8ea280a612b91a582869 and later.

## References
- https://seclists.org/bugtraq/2019/May/60
- http://www.securityfocus.com/bid/104896
- https://www.debian.org/security/2019/dsa-4449
- https://github.com/FFmpeg/FFmpeg/commit/2b46ebdbff1d8dec7a3d8ea280a612b91a582869
