# [H] CVE-2021-36773

## Summary
Severity: High
Advisory: CVE-2021-36773
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-18
Source: https://osv.dev/vulnerability/CVE-2021-36773
Type: osv

## Details
uBlock Origin before 1.36.2 and nMatrix before 4.4.9 support an arbitrary depth of parameter nesting for strict blocking, which allows crafted web sites to cause a denial of service (unbounded recursion that can trigger memory consumption and a loss of all blocking functionality).

## References
- https://lists.debian.org/debian-lts-announce/2022/06/msg00024.html
- https://news.ycombinator.com/item?id=27833752
- https://github.com/vtriolet/writings/blob/main/posts/2021/ublock_origin_and_umatrix_denial_of_service.adoc
