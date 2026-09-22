# [C] CVE-2016-9536

## Summary
Severity: Critical
Advisory: CVE-2016-9536
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-11-22
Source: https://osv.dev/vulnerability/CVE-2016-9536
Type: osv

## Details
tools/tiff2pdf.c in libtiff 4.0.6 has out-of-bounds write vulnerabilities in heap allocated buffers in t2p_process_jpeg_strip(). Reported as MSVR 35098, aka "t2p_process_jpeg_strip heap-buffer-overflow."

## References
- http://www.securityfocus.com/bid/94745
- http://rhn.redhat.com/errata/RHSA-2017-0225.html
- http://www.debian.org/security/2017/dsa-3762
- http://www.securityfocus.com/bid/94484
- https://github.com/vadz/libtiff/commit/83a4b92815ea04969d494416eaae3d4c6b338e4a#diff-5173a9b3b48146e4fd86d7b9b346115e
