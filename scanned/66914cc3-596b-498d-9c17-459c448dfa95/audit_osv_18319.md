# [H] CVE-2020-26148

## Summary
Severity: High
Advisory: CVE-2020-26148
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-30
Source: https://osv.dev/vulnerability/CVE-2020-26148
Type: osv

## Details
md_push_block_bytes in md4c.c in md4c 0.4.5 allows attackers to trigger use of uninitialized memory, and cause a denial of service (e.g., assertion failure) via a malformed Markdown document.

## References
- https://github.com/mity/md4c/issues/130
