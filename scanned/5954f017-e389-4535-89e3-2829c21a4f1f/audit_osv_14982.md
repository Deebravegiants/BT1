# [H] CVE-2019-12802

## Summary
Severity: High
Advisory: CVE-2019-12802
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-06-13
Source: https://osv.dev/vulnerability/CVE-2019-12802
Type: osv

## Details
In radare2 through 3.5.1, the rcc_context function of libr/egg/egg_lang.c mishandles changing context. This allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact (invalid memory access in r_egg_lang_parsechar; invalid free in rcc_pusharg).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IEXZWAMVKGZKHALV4IVWQS2ORJKRH57U/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SX4TLTE75VYUGSPYEKMYFPUZMRDIR7O2/
- https://github.com/radare/radare2/issues/14296
