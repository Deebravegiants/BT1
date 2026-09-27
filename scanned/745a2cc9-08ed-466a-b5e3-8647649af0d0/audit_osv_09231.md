# [H] CVE-2016-9114

## Summary
Severity: High
Advisory: CVE-2016-9114
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-10-30
Source: https://osv.dev/vulnerability/CVE-2016-9114
Type: osv

## Details
There is a NULL Pointer Access in function imagetopnm of convert.c:1943(jp2) of OpenJPEG 2.1.2. image->comps[compno].data is not assigned a value after initialization(NULL). Impact is Denial of Service.

## References
- http://www.securityfocus.com/bid/93979
- https://security.gentoo.org/glsa/201710-26
- https://github.com/uclouvain/openjpeg/issues/857
