# [H] CVE-2017-15056

## Summary
Severity: High
Advisory: CVE-2017-15056
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-10-06
Source: https://osv.dev/vulnerability/CVE-2017-15056
Type: osv

## Details
p_lx_elf.cpp in UPX 3.94 mishandles ELF headers, which allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted binary file, as demonstrated by an Invalid Pointer Read in PackLinuxElf64::unpack().

## References
- https://github.com/upx/upx/issues/128
