# [H] CVE-2023-31973

## Summary
Severity: High
Advisory: CVE-2023-31973
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-05-09
Source: https://osv.dev/vulnerability/CVE-2023-31973
Type: osv

## Details
yasm v1.3.0 was discovered to contain a use after free via the function expand_mmac_params at /nasm/nasm-pp.c. Note: Multiple third parties dispute this as a bug and not a vulnerability according to the YASM security policy.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31973.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-31973
- https://github.com/yasm/yasm/issues/207
