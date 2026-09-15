# [M] CVE-2021-20285

## Summary
Severity: Medium
Advisory: CVE-2021-20285
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2021-03-26
Source: https://osv.dev/vulnerability/CVE-2021-20285
Type: osv

## Details
A flaw was found in upx canPack in p_lx_elf.cpp in UPX 3.96. This flaw allows attackers to cause a denial of service (SEGV or buffer overflow and application crash) or possibly have unspecified other impacts via a crafted ELF. The highest threat from this vulnerability is to system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1937787
- https://github.com/upx/upx/issues/421
