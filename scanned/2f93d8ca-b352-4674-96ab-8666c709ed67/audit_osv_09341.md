# [C] CVE-2016-9534

## Summary
Severity: Critical
Advisory: CVE-2016-9534
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-11-22
Source: https://osv.dev/vulnerability/CVE-2016-9534
Type: osv

## Details
tif_write.c in libtiff 4.0.6 has an issue in the error code path of TIFFFlushData1() that didn't reset the tif_rawcc and tif_rawcp members. Reported as MSVR 35095, aka "TIFFFlushData1 heap-buffer-overflow."

## References
- http://www.securityfocus.com/bid/94743
- http://rhn.redhat.com/errata/RHSA-2017-0225.html
- http://www.debian.org/security/2017/dsa-3762
- http://www.securityfocus.com/bid/94484
- https://github.com/vadz/libtiff/commit/83a4b92815ea04969d494416eaae3d4c6b338e4a#diff-5be5ce02d0dea67050d5b2a10102d1ba
