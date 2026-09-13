# [M] CVE-2021-40942

## Summary
Severity: Medium
Advisory: CVE-2021-40942
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-06-27
Source: https://osv.dev/vulnerability/CVE-2021-40942
Type: osv

## Details
In GPAC MP4Box v1.1.0, there is a heap-buffer-overflow in the function filter_parse_dyn_args function in filter_core/filter.c:1454, as demonstrated by GPAC. This can cause a denial of service (DOS).

## References
- https://github.com/gpac/gpac/issues/1908
