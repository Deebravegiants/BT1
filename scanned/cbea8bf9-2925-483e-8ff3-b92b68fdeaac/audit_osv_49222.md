# [M] CVE-2018-6612

## Summary
Severity: Medium
Advisory: CVE-2018-6612
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-04
Source: https://osv.dev/vulnerability/CVE-2018-6612
Type: osv

## Details
An integer underflow bug in the process_EXIF function of the exif.c file of jhead 3.00 raises a heap-based buffer over-read when processing a malicious JPEG file, which may allow a remote attacker to cause a denial-of-service attack or unspecified other impact.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=889272
- https://launchpad.net/ubuntu/+source/jhead/1:3.00-6
