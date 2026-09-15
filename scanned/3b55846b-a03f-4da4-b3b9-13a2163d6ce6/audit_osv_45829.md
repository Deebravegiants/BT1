# [H] JLSEC-2026-380

## Summary
Severity: High
Advisory: JLSEC-2026-380
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/JLSEC-2026-380
Type: osv

## Affected
- Julia: `Expat_jll` — affected >=0 <2.7.5+0

## Details
In libexpat before 2.7.4, the doContent function does not properly determine the buffer size bufSize because there is no integer overflow check for tag buffer reallocation.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://github.com/libexpat/libexpat/pull/1075
- https://github.com/libexpat/libexpat/pull/1075/commits/9c2d990389e6abe2e44527eeaa8b39f16fe859c7
