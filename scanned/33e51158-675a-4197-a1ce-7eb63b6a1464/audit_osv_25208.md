# [M] CVE-2023-31972

## Summary
Severity: Medium
Advisory: CVE-2023-31972
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-05-09
Source: https://osv.dev/vulnerability/CVE-2023-31972
Type: osv

## Details
yasm v1.3.0 was discovered to contain a use after free via the function pp_getline at /nasm/nasm-pp.c. Note: Multiple third parties dispute this as a bug and not a vulnerability according to the YASM security policy.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31972.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-31972
- https://github.com/yasm/yasm/issues/209
