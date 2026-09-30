# [C] CVE-2022-43705

## Summary
Severity: Critical
Advisory: CVE-2022-43705
Aliases: GHSA-4v9w-qvcq-6q7w
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-11-27
Source: https://osv.dev/vulnerability/CVE-2022-43705
Type: osv

## Details
In Botan before 2.19.3, it is possible to forge OCSP responses due to a certificate verification error. This issue was introduced in Botan 1.11.34 (November 2016).

## References
- https://github.com/randombit/botan/releases/tag/2.19.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/43xxx/CVE-2022-43705.json
- https://github.com/randombit/botan/security/advisories/GHSA-4v9w-qvcq-6q7w
- https://nvd.nist.gov/vuln/detail/CVE-2022-43705
