# [H] CVE-2018-11416

## Summary
Severity: High
Advisory: CVE-2018-11416
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-05-24
Source: https://osv.dev/vulnerability/CVE-2018-11416
Type: osv

## Details
jpegoptim.c in jpegoptim 1.4.5 (fixed in 1.4.6) has an invalid use of realloc() and free(), which allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact.

## References
- https://github.com/tjko/jpegoptim/blob/master/README
- https://github.com/tjko/jpegoptim/issues/57
