# [H] CVE-2017-16357

## Summary
Severity: High
Advisory: CVE-2017-16357
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-11-01
Source: https://osv.dev/vulnerability/CVE-2017-16357
Type: osv

## Details
In radare 2.0.1, a memory corruption vulnerability exists in store_versioninfo_gnu_verdef() and store_versioninfo_gnu_verneed() in libr/bin/format/elf/elf.c, as demonstrated by an invalid free. This error is due to improper sh_size validation when allocating memory.

## References
- https://github.com/radare/radare2/commit/0b973e28166636e0ff1fad80baa0385c9c09c53a
- https://github.com/radare/radare2/issues/8742
