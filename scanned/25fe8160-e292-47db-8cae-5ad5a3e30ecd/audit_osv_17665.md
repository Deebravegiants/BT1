# [M] CVE-2020-18781

## Summary
Severity: Medium
Advisory: CVE-2020-18781
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-08-22
Source: https://osv.dev/vulnerability/CVE-2020-18781
Type: osv

## Details
Heap buffer overflow vulnerability in FilePOSIX::read in File.cpp in audiofile 0.3.6 may cause denial-of-service via a crafted wav file, this bug can be triggered by the executable sfconvert.

## References
- https://github.com/mpruett/audiofile/issues/56
