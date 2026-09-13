# [M] CVE-2018-8098

## Summary
Severity: Medium
Advisory: CVE-2018-8098
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-14
Source: https://osv.dev/vulnerability/CVE-2018-8098
Type: osv

## Details
Integer overflow in the index.c:read_entry() function while decompressing a compressed prefix length in libgit2 before v0.26.2 allows an attacker to cause a denial of service (out-of-bounds read) via a crafted repository index file.

## References
- https://lists.debian.org/debian-lts-announce/2022/03/msg00031.html
- https://github.com/libgit2/libgit2/commit/3207ddb0103543da8ad2139ec6539f590f9900c1
- https://github.com/libgit2/libgit2/commit/3db1af1f370295ad5355b8f64b865a2a357bcac0
- https://libgit2.github.com/security/
