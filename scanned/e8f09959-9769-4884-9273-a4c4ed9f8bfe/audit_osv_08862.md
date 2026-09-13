# [C] CVE-2016-6354

## Summary
Severity: Critical
Advisory: CVE-2016-6354
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/CVE-2016-6354
Type: osv

## Details
Heap-based buffer overflow in the yy_get_next_buffer function in Flex before 2.6.1 might allow context-dependent attackers to cause a denial of service or possibly execute arbitrary code via vectors involving num_to_read.

## References
- http://www.debian.org/security/2016/dsa-3653
- http://www.openwall.com/lists/oss-security/2016/07/18/8
- http://www.openwall.com/lists/oss-security/2016/07/26/12
- https://security.gentoo.org/glsa/201701-31
- https://github.com/westes/flex/commit/a5cbe929ac3255d371e698f62dc256afe7006466
