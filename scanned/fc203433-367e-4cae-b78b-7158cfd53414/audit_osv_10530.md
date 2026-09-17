# [H] CVE-2017-16869

## Summary
Severity: High
Advisory: CVE-2017-16869
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-11-17
Source: https://osv.dev/vulnerability/CVE-2017-16869
Type: osv

## Details
p_mach.cpp in UPX 3.94 allows remote attackers to cause a denial of service (invalid memory access and application crash) or possibly have unspecified other impact via a crafted Mach-O file, related to canPack and unpack functions. NOTE: the vendor has stated "there is no security implication whatsoever.

## References
- https://github.com/upx/upx/issues/146
