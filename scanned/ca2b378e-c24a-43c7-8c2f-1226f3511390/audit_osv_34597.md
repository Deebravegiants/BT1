# [C] Taiga Authenticated Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2025-62368
Aliases: GHSA-cpcf-9276-fwc5
CVSS: 9.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-62368
Type: osv

## Details
Taiga is an open source project management platform. In versions 6.8.3 and earlier, a remote code execution vulnerability exists in the Taiga API due to unsafe deserialization of untrusted data. This issue is fixed in version 6.9.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62368.json
- https://github.com/taigaio/taiga-back/security/advisories/GHSA-cpcf-9276-fwc5
- https://nvd.nist.gov/vuln/detail/CVE-2025-62368
