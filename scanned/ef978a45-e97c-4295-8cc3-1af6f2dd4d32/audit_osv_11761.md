# [H] CVE-2017-9527

## Summary
Severity: High
Advisory: CVE-2017-9527
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-06-11
Source: https://osv.dev/vulnerability/CVE-2017-9527
Type: osv

## Details
The mark_context_stack function in gc.c in mruby through 1.2.0 allows attackers to cause a denial of service (heap-based use-after-free and application crash) or possibly have unspecified other impact via a crafted .rb file.

## References
- https://lists.debian.org/debian-lts-announce/2022/05/msg00006.html
- https://github.com/mruby/mruby/commit/5c114c91d4ff31859fcd84cf8bf349b737b90d99
- https://github.com/mruby/mruby/issues/3486
