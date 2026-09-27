# [H] CVE-2017-14749

## Summary
Severity: High
Advisory: CVE-2017-14749
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-26
Source: https://osv.dev/vulnerability/CVE-2017-14749
Type: osv

## Details
JerryScript 1.0 allows remote attackers to cause a denial of service (jmem_heap_alloc_block_internal heap memory corruption) or possibly execute arbitrary code via a crafted .js file, because unrecognized \ characters cause incorrect 0x00 characters in bytecode.literal data.

## References
- https://github.com/jerryscript-project/jerryscript/issues/2008
