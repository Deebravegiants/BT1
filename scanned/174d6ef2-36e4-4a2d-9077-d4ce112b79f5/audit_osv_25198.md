# [H] CVE-2023-31906

## Summary
Severity: High
Advisory: CVE-2023-31906
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-05-10
Source: https://osv.dev/vulnerability/CVE-2023-31906
Type: osv

## Details
Jerryscript 3.0.0(commit 1a2c047) was discovered to contain a heap-buffer-overflow via the component lexer_compare_identifier_to_chars at /jerry-core/parser/js/js-lexer.c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31906.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-31906
- https://github.com/jerryscript-project/jerryscript/issues/5066
