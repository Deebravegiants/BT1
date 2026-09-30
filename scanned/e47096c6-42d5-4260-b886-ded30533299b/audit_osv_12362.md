# [H] CVE-2018-11498

## Summary
Severity: High
Advisory: CVE-2018-11498
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-05-26
Source: https://osv.dev/vulnerability/CVE-2018-11498
Type: osv

## Details
In Lizard v1.0 and LZ5 v2.0 (the prior release, before the product was renamed), there is an unchecked buffer size during a memcpy in the Lizard_decompress_LIZv1 function (lib/lizard_decompress_liz.h). Remote attackers can leverage this vulnerability to cause a denial of service via a crafted input file, as well as achieve remote code execution.

## References
- https://github.com/inikep/lizard/issues/16
