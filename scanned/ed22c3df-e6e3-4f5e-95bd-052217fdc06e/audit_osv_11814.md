# [M] CVE-2017-9847

## Summary
Severity: Medium
Advisory: CVE-2017-9847
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-24
Source: https://osv.dev/vulnerability/CVE-2017-9847
Type: osv

## Details
The bdecode function in bdecode.cpp in libtorrent 1.1.3 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted file.

## References
- https://github.com/arvidn/libtorrent/issues/2099
