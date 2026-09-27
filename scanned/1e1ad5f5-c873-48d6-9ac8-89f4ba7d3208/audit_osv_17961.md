# [M] CVE-2020-22033

## Summary
Severity: Medium
Advisory: CVE-2020-22033
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2020-22033
Type: osv

## Details
A heap-based Buffer Overflow Vulnerability exists FFmpeg 4.2 at libavfilter/vf_vmafmotion.c in convolution_y_8bit, which could let a remote malicious user cause a Denial of Service.

## References
- https://cwe.mitre.org/data/definitions/122.html
- https://www.debian.org/security/2021/dsa-4990
- https://trac.ffmpeg.org/ticket/8246
