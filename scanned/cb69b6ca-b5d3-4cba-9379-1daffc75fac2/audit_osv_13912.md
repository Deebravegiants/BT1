# [M] CVE-2018-5252

## Summary
Severity: Medium
Advisory: CVE-2018-5252
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-05
Source: https://osv.dev/vulnerability/CVE-2018-5252
Type: osv

## Details
libimageworsener.a in ImageWorsener 1.3.2, when libjpeg 8d is used, has a large loop in the get_raw_sample_int function in imagew-main.c.

## References
- https://github.com/jsummers/imageworsener/issues/34
