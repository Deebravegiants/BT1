# [M] CVE-2017-9260

## Summary
Severity: Medium
Advisory: CVE-2017-9260
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-27
Source: https://osv.dev/vulnerability/CVE-2017-9260
Type: osv

## Details
The TDStretchSSE::calcCrossCorr function in source/SoundTouch/sse_optimized.cpp in SoundTouch 1.9.2 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted wav file.

## References
- https://www.exploit-db.com/exploits/42389/
- http://seclists.org/fulldisclosure/2017/Jul/62
