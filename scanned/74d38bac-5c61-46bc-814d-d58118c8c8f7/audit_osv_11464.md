# [M] CVE-2017-7946

## Summary
Severity: Medium
Advisory: CVE-2017-7946
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-18
Source: https://osv.dev/vulnerability/CVE-2017-7946
Type: osv

## Details
The get_relocs_64 function in libr/bin/format/mach0/mach0.c in radare2 1.3.0 allows remote attackers to cause a denial of service (use-after-free and application crash) via a crafted Mach0 file.

## References
- https://github.com/radare/radare2/commit/d1e8ac62c6d978d4662f69116e30230d43033c92
- https://github.com/radare/radare2/issues/7301
