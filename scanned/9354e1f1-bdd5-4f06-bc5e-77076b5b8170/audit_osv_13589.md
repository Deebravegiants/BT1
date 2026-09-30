# [M] CVE-2018-20458

## Summary
Severity: Medium
Advisory: CVE-2018-20458
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-25
Source: https://osv.dev/vulnerability/CVE-2018-20458
Type: osv

## Details
In radare2 prior to 3.1.1, r_bin_dyldcache_extract in libr/bin/format/mach0/dyldcache.c may allow attackers to cause a denial-of-service (application crash caused by out-of-bounds read) by crafting an input file.

## References
- https://github.com/radareorg/radare2/commit/30f4c7b52a4e2dc0d0b1bae487d90f5437c69d19
- https://github.com/radare/radare2/issues/12374
