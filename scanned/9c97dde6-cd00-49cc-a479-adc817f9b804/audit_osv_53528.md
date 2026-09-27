# [H] CVE-2022-47069

## Summary
Severity: High
Advisory: CVE-2022-47069
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-08-22
Source: https://osv.dev/vulnerability/CVE-2022-47069
Type: osv

## Details
p7zip 16.02 was discovered to contain a heap-buffer-overflow vulnerability via the function NArchive::NZip::CInArchive::FindCd(bool) at CPP/7zip/Archive/Zip/ZipIn.cpp. NOTE: the Supplier has found that this is not a buffer overflow; at most an out-of-bounds read can occur.

## References
- https://sourceforge.net/p/p7zip/bugs/241/
