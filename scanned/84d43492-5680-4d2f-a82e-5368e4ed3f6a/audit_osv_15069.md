# [C] CVE-2019-13224

## Summary
Severity: Critical
Advisory: CVE-2019-13224
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-10
Source: https://osv.dev/vulnerability/CVE-2019-13224
Type: osv

## Details
A use-after-free in onig_new_deluxe() in regext.c in Oniguruma 6.9.2 allows attackers to potentially cause information disclosure, denial of service, or possibly code execution by providing a crafted regular expression. The attacker provides a pair of a regex pattern and a string, with a multi-byte encoding that gets handled by onig_new_deluxe(). Oniguruma issues often affect Ruby, as well as common optional libraries for PHP and Rust.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JWCPDTZOIUKGMFAD5NAKUB7FPJFAIQN5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SNL26OZSQRVLEO6JRNUVIMZTICXBNEQW/
- https://support.f5.com/csp/article/K00103182?utm_source=f5support&amp%3Butm_medium=RSS
- https://lists.debian.org/debian-lts-announce/2019/07/msg00013.html
- https://security.gentoo.org/glsa/201911-03
- https://support.f5.com/csp/article/K00103182
- https://usn.ubuntu.com/4088-1/
- https://github.com/kkos/oniguruma/commit/0f7f61ed1b7b697e283e37bd2d731d0bd57adb55
