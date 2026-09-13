# [H] CVE-2019-12829

## Summary
Severity: High
Advisory: CVE-2019-12829
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-06-15
Source: https://osv.dev/vulnerability/CVE-2019-12829
Type: osv

## Details
radare2 through 3.5.1 mishandles the RParse API, which allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact, as demonstrated by newstr buffer overflows during replace operations. This affects libr/asm/asm.c and libr/parse/parse.c.

## References
- https://github.com/radare/radare2/issues/14303
