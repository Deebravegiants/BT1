# [C] CVE-2020-1900

## Summary
Severity: Critical
Advisory: CVE-2020-1900
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-11
Source: https://osv.dev/vulnerability/CVE-2020-1900
Type: osv

## Details
When unserializing an object with dynamic properties HHVM needs to pre-reserve the full size of the dynamic property array before inserting anything into it. Otherwise the array might resize, invalidating previously stored references. This pre-reservation was not occurring in HHVM prior to v4.32.3, between versions 4.33.0 and 4.56.0, 4.57.0, 4.58.0, 4.58.1, 4.59.0, 4.60.0, 4.61.0, 4.62.0.

## References
- https://hhvm.com/blog/2020/06/30/security-update.html
- https://github.com/facebook/hhvm/commit/c1c4bb0cf9e076aafaf4ff3515556ef9faf906f3
