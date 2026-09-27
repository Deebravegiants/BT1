# [C] CVE-2023-25933

## Summary
Severity: Critical
Advisory: CVE-2023-25933
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-18
Source: https://osv.dev/vulnerability/CVE-2023-25933
Type: osv

## Details
A type confusion bug in TypedArray prior to commit e6ed9c1a4b02dc219de1648f44cd808a56171b81 could have been used by a malicious attacker to execute arbitrary code via untrusted JavaScript. Note that this is only exploitable in cases where Hermes is used to execute untrusted JavaScript. Hence, most React Native applications are not affected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25933.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-25933
- https://www.facebook.com/security/advisories/cve-2023-25933
- https://github.com/facebook/hermes/commit/e6ed9c1a4b02dc219de1648f44cd808a56171b81
