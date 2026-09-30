# [C] CVE-2016-9535

## Summary
Severity: Critical
Advisory: CVE-2016-9535
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-11-22
Source: https://osv.dev/vulnerability/CVE-2016-9535
Type: osv

## Details
tif_predict.h and tif_predict.c in libtiff 4.0.6 have assertions that can lead to assertion failures in debug mode, or buffer overflows in release mode, when dealing with unusual tile size like YCbCr with subsampling. Reported as MSVR 35105, aka "Predictor heap-buffer-overflow."

## References
- http://www.securityfocus.com/bid/94744
- http://rhn.redhat.com/errata/RHSA-2017-0225.html
- http://www.debian.org/security/2017/dsa-3844
- http://www.securityfocus.com/bid/94484
- https://github.com/vadz/libtiff/commit/3ca657a8793dd011bf869695d72ad31c779c3cc1
- https://github.com/vadz/libtiff/commit/6a984bf7905c6621281588431f384e79d11a2e33
