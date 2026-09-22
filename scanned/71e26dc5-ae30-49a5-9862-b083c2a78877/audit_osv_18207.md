# [H] CVE-2020-24994

## Summary
Severity: High
Advisory: CVE-2020-24994
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-03-23
Source: https://osv.dev/vulnerability/CVE-2020-24994
Type: osv

## Details
Stack overflow in the parse_tag function in libass/ass_parse.c in libass before 0.15.0 allows remote attackers to cause a denial of service or remote code execution via a crafted file.

## References
- https://github.com/libass/libass/issues/423
- https://github.com/libass/libass/commit/6835731c2fe4164a0c50bc91d12c43b2a2b4e
- https://github.com/libass/libass/issues/422
- https://github.com/libass/libass/issues/422#issuecomment-806002919
