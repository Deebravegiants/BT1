# [H] CVE-2023-26266

## Summary
Severity: High
Advisory: CVE-2023-26266
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-02-21
Source: https://osv.dev/vulnerability/CVE-2023-26266
Type: osv

## Details
In AFL++ 4.05c, the CmpLog component uses the current working directory to resolve and execute unprefixed fuzzing targets, allowing code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26266.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-26266
- https://github.com/AFLplusplus/AFLplusplus/pull/1643
