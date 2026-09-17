# [C] CVE-2023-23557

## Summary
Severity: Critical
Advisory: CVE-2023-23557
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-18
Source: https://osv.dev/vulnerability/CVE-2023-23557
Type: osv

## Details
An error in Hermes' algorithm for copying objects properties prior to commit a00d237346894c6067a594983be6634f4168c9ad could be used by a malicious attacker to execute arbitrary code via type confusion. Note that this is only exploitable in cases where Hermes is used to execute untrusted JavaScript. Hence, most React Native applications are not affected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23557.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-23557
- https://www.facebook.com/security/advisories/cve-2023-23557
- https://github.com/facebook/hermes/commit/a00d237346894c6067a594983be6634f4168c9ad
