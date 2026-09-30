# [H] CVE-2017-15385

## Summary
Severity: High
Advisory: CVE-2017-15385
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-10-16
Source: https://osv.dev/vulnerability/CVE-2017-15385
Type: osv

## Details
The store_versioninfo_gnu_verdef function in libr/bin/format/elf/elf.c in radare2 2.0.0 allows remote attackers to cause a denial of service (r_read_le16 invalid write and application crash) or possibly have unspecified other impact via a crafted ELF file.

## References
- https://github.com/radare/radare2/issues/8685
- https://github.com/radare/radare2/commit/21a6f570ba33fa9f52f1bba87f07acc4e8c178f4
