# [H] CVE-2023-24833

## Summary
Severity: High
Advisory: CVE-2023-24833
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-05-18
Source: https://osv.dev/vulnerability/CVE-2023-24833
Type: osv

## Details
A use-after-free in BigIntPrimitive addition in Hermes prior to commit a6dcafe6ded8e61658b40f5699878cd19a481f80 could have been used by an attacker to leak raw data from Hermes VM’s heap. Note that this is only exploitable in cases where Hermes is used to execute untrusted JavaScript. Hence, most React Native applications are not affected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24833.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-24833
- https://www.facebook.com/security/advisories/cve-2023-24833
- https://github.com/facebook/hermes/commit/a6dcafe6ded8e61658b40f5699878cd19a481f80
