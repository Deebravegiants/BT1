# [C] CVE-2017-5209

## Summary
Severity: Critical
Advisory: CVE-2017-5209
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-01-11
Source: https://osv.dev/vulnerability/CVE-2017-5209
Type: osv

## Details
The base64decode function in base64.c in libimobiledevice libplist through 1.12 allows attackers to obtain sensitive information from process memory or cause a denial of service (buffer over-read) via split encoded Apple Property List data.

## References
- https://lists.debian.org/debian-lts-announce/2020/04/msg00002.html
- http://www.securityfocus.com/bid/95385
- https://github.com/libimobiledevice/libplist/commit/3a55ddd3c4c11ce75a86afbefd085d8d397ff957
