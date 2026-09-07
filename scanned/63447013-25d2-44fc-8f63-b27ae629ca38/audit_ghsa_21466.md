# [M] Leak in Aliyun  KeySecret 

## Summary
Severity: Medium
Advisory: GHSA-3w3h-7xgx-grwc
CVE: CVE-2022-39397
CWE: CWE-200
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:P/AC:L/PR:H/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-3w3h-7xgx-grwc
Type: github-advisory

## Affected
- crates.io: `aliyun-oss-client` — affected >=0 <0.8.1

## Details
### Impact
Users of this library will be affected when using this library, the incoming secret will be disclosed unintentionally.

### Patches
This have already been solved.

### Workarounds
No, It cannot be patched without upgrading

### References
No

### For more information
If you have any questions or comments about this advisory:
* Email us at [email address](mailto:772364230@qq.com)

## References
- https://github.com/tu6ge/oss-rs/security/advisories/GHSA-3w3h-7xgx-grwc
- https://nvd.nist.gov/vuln/detail/CVE-2022-39397
- https://github.com/tu6ge/oss-rs/commit/e4553f7d74fce682d802f8fb073943387796df29
- https://github.com/tu6ge/oss-rs
- https://rustsec.org/advisories/RUSTSEC-2022-0089.html
