# [M] CVE-2017-9520

## Summary
Severity: Medium
Advisory: CVE-2017-9520
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-08
Source: https://osv.dev/vulnerability/CVE-2017-9520
Type: osv

## Details
The r_config_set function in libr/config/config.c in radare2 1.5.0 allows remote attackers to cause a denial of service (use-after-free and application crash) via a crafted DEX file.

## References
- https://github.com/radare/radare2/issues/7698
- https://github.com/radare/radare2/commit/f85bc674b2a2256a364fe796351bc1971e106005
