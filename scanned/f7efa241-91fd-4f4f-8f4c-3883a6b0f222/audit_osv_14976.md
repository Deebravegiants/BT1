# [H] CVE-2019-12790

## Summary
Severity: High
Advisory: CVE-2019-12790
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-06-10
Source: https://osv.dev/vulnerability/CVE-2019-12790
Type: osv

## Details
In radare2 through 3.5.1, there is a heap-based buffer over-read in the r_egg_lang_parsechar function of egg_lang.c. This allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact because of missing length validation in libr/egg/egg.c.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IEXZWAMVKGZKHALV4IVWQS2ORJKRH57U/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SX4TLTE75VYUGSPYEKMYFPUZMRDIR7O2/
- https://github.com/radare/radare2/issues/14211
