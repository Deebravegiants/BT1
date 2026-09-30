# [H] CVE-2018-17942

## Summary
Severity: High
Advisory: CVE-2018-17942
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-10-03
Source: https://osv.dev/vulnerability/CVE-2018-17942
Type: osv

## Details
The convert_to_decimal function in vasnprintf.c in Gnulib before 2018-09-23 has a heap-based buffer overflow because memory is not allocated for a trailing '\0' character during %f processing.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/A5UQRNQE6XHMD5UYYHAU3VQWAYHIPMQS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TMGHTVYH3KAFN34QXNSGEQDSTV7MCOQW/
- https://github.com/coreutils/gnulib/commit/278b4175c9d7dd47c1a3071554aac02add3b3c35
- https://lists.gnu.org/archive/html/bug-gnulib/2018-09/msg00107.html
- https://savannah.gnu.org/bugs/?func=detailitem&item_id=54686
