# [C] CVE-2017-7614

## Summary
Severity: Critical
Advisory: CVE-2017-7614
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-09
Source: https://osv.dev/vulnerability/CVE-2017-7614
Type: osv

## Details
elflink.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.28, has a "member access within null pointer" undefined behavior issue, which might allow remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via an "int main() {return 0;}" program.

## References
- https://security.gentoo.org/glsa/201709-02
- https://blogs.gentoo.org/ago/2017/04/05/binutils-two-null-pointer-dereference-in-elflink-c/
