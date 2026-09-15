# [C] CVE-2023-23556

## Summary
Severity: Critical
Advisory: CVE-2023-23556
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-18
Source: https://osv.dev/vulnerability/CVE-2023-23556
Type: osv

## Details
An error in BigInt conversion to Number in Hermes prior to commit a6dcafe6ded8e61658b40f5699878cd19a481f80 could have been used by a malicious attacker to execute arbitrary code due to an out-of-bound write. Note that this bug is only exploitable in cases where Hermes is used to execute untrusted JavaScript. Hence, most React Native applications are not affected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23556.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-23556
- https://www.facebook.com/security/advisories/cve-2023-23556
- https://github.com/facebook/hermes/commit/a6dcafe6ded8e61658b40f5699878cd19a481f80
