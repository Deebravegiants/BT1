# [H] CVE-2024-37795

## Summary
Severity: High
Advisory: CVE-2024-37795
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-17
Source: https://osv.dev/vulnerability/CVE-2024-37795
Type: osv

## Details
A segmentation fault in CVC5 Solver v1.1.3 allows attackers to cause a Denial of Service (DoS) via a crafted SMT-LIB input file containing the `set-logic` command with specific formatting errors.

## References
- https://github.com/cvc5/cvc5/issues/10813
