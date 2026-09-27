# [M] CVE-2025-12829

## Summary
Severity: Medium
Advisory: CVE-2025-12829
Aliases: GHSA-7mgf-6x73-5h7r
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-11-07
Source: https://osv.dev/vulnerability/CVE-2025-12829
Type: osv

## Details
An uninitialized stack read issue exists in Amazon Ion-C versions <v1.1.4 that may allow a threat actor to craft data and serialize it to Ion text in such a way that sensitive data in memory could be exposed through UTF-8 escape sequences. To mitigate this issue, users should upgrade to version v1.1.4.

## References
- https://aws.amazon.com/security/security-bulletins/AWS-2025-027/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/12xxx/CVE-2025-12829.json
- https://github.com/amazon-ion/ion-c/security/advisories/GHSA-7mgf-6x73-5h7r
- https://nvd.nist.gov/vuln/detail/CVE-2025-12829
- https://github.com/amazon-ion/ion-c/releases/tag/v1.1.4
