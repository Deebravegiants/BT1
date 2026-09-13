# [C] CVE-2017-17479

## Summary
Severity: Critical
Advisory: CVE-2017-17479
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-08
Source: https://osv.dev/vulnerability/CVE-2017-17479
Type: osv

## Details
In OpenJPEG 2.3.0, a stack-based buffer overflow was discovered in the pgxtoimage function in jpwl/convert.c. The vulnerability causes an out-of-bounds write, which may lead to remote denial of service or possibly remote code execution.

## References
- https://github.com/uclouvain/openjpeg/issues/1044
