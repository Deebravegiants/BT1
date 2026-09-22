# [M] CVE-2022-44318

## Summary
Severity: Medium
Advisory: CVE-2022-44318
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-11-08
Source: https://osv.dev/vulnerability/CVE-2022-44318
Type: osv

## Details
PicoC Version 3.2.2 was discovered to contain a heap buffer overflow in the StringStrcat function in cstdlib/string.c when called from ExpressionParseFunctionCall.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/44xxx/CVE-2022-44318.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-44318
- https://github.com/jpoirier/picoc/issues/37
- https://gitlab.com/zsaleeba/picoc/-/issues/48
