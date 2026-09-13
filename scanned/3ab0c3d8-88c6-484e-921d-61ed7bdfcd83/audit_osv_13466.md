# [M] CVE-2018-1999013

## Summary
Severity: Medium
Advisory: CVE-2018-1999013
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2018-07-23
Source: https://osv.dev/vulnerability/CVE-2018-1999013
Type: osv

## Details
FFmpeg before commit a7e032a277452366771951e29fd0bf2bd5c029f0 contains a use-after-free vulnerability in the realmedia demuxer that can result in vulnerability allows attacker to read heap memory. This attack appear to be exploitable via specially crafted RM file has to be provided as input. This vulnerability appears to have been fixed in a7e032a277452366771951e29fd0bf2bd5c029f0 and later.

## References
- http://www.securityfocus.com/bid/104896
- https://github.com/FFmpeg/FFmpeg/commit/a7e032a277452366771951e29fd0bf2bd5c029f0
