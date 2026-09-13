# [M] CVE-2023-29582

## Summary
Severity: Medium
Advisory: CVE-2023-29582
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/CVE-2023-29582
Type: osv

## Details
yasm 1.3.0.55.g101bc was discovered to contain a stack overflow via the function parse_expr1 at /nasm/nasm-parse.c. Note: This has been disputed by third parties who argue this is a bug and not a security issue because yasm is a standalone program not designed to run untrusted code.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2189601#c3
- https://github.com/yasm/yasm/issues/217
- https://github.com/z1r00/fuzz_vuln/blob/main/yasm/stack-overflow/parse_expr1/readme.md
