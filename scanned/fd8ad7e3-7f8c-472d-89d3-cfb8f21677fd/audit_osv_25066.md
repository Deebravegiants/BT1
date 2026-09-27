# [C] CVE-2023-30470

## Summary
Severity: Critical
Advisory: CVE-2023-30470
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-18
Source: https://osv.dev/vulnerability/CVE-2023-30470
Type: osv

## Details
A use-after-free related to unsound inference in the bytecode generation when optimizations are enabled for Hermes prior to commit da8990f737ebb9d9810633502f65ed462b819c09 could have been used by an attacker to achieve remote code execution. Note that this is only exploitable in cases where Hermes is used to execute untrusted JavaScript. Hence, most React Native applications are not affected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30470.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-30470
- https://www.facebook.com/security/advisories/cve-2023-30470
- https://github.com/facebook/hermes/commit/da8990f737ebb9d9810633502f65ed462b819c09
