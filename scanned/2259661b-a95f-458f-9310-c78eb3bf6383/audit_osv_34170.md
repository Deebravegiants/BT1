# [C] GenX_FX authentication bypass in JWT validation

## Summary
Severity: Critical
Advisory: CVE-2025-55306
Aliases: GHSA-2xjq-pvwj-mvm6
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-55306
Type: osv

## Details
GenX_FX is an advance IA trading platform that will focus on forex trading. A vulnerability was identified in the GenX FX backend where API keys and authentication tokens may be exposed if environment variables are misconfigured. Unauthorized users could gain access to cloud resources (Google Cloud, Firebase, GitHub, etc.).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55306.json
- https://github.com/Mouy-leng/GenX_FX/security/advisories/GHSA-2xjq-pvwj-mvm6
- https://nvd.nist.gov/vuln/detail/CVE-2025-55306
