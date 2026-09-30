# [M] CVE-2021-30027

## Summary
Severity: Medium
Advisory: CVE-2021-30027
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-29
Source: https://osv.dev/vulnerability/CVE-2021-30027
Type: osv

## Details
md_analyze_line in md4c.c in md4c 0.4.7 allows attackers to trigger use of uninitialized memory, and cause a denial of service via a malformed Markdown document.

## References
- https://github.com/mity/md4c/issues/155
- https://github.com/mity/md4c/commit/4fc808d8fe8d8904f8525bb4231d854f45e23a19
