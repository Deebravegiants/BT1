# [M] CVE-2019-13225

## Summary
Severity: Medium
Advisory: CVE-2019-13225
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-10
Source: https://osv.dev/vulnerability/CVE-2019-13225
Type: osv

## Details
A NULL Pointer Dereference in match_at() in regexec.c in Oniguruma 6.9.2 allows attackers to potentially cause denial of service by providing a crafted regular expression. Oniguruma issues often affect Ruby, as well as common optional libraries for PHP and Rust.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JWCPDTZOIUKGMFAD5NAKUB7FPJFAIQN5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SNL26OZSQRVLEO6JRNUVIMZTICXBNEQW/
- https://security.gentoo.org/glsa/201911-03
- https://github.com/kkos/oniguruma/commit/c509265c5f6ae7264f7b8a8aae1cfa5fc59d108c
