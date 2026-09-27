# [C] CVE-2022-36938

## Summary
Severity: Critical
Advisory: CVE-2022-36938
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-10
Source: https://osv.dev/vulnerability/CVE-2022-36938
Type: osv

## Details
DexLoader function get_stringidx_fromdex() in Redex prior to commit 3b44c64 can load an out of bound address when loading the string index table, potentially allowing remote code execution during processing of a 3rd party Android APK file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/36xxx/CVE-2022-36938.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-36938
- https://github.com/facebook/redex/commit/3b44c640346b77bfb7ef36e2413688dd460288d2
