# [C] fosrl Pangolin - Access Token Scope Bypass Allows Cross-Resource Authentication

## Summary
Severity: Critical
Advisory: CVE-2026-72564
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72564
Type: osv

## Details
An improper authorization vulnerability in fosrl/pangolin through v1.20.0 allows an authenticated remote attacker to authenticate to any resource in any organization by reusing an access token issued for a different resource.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72564.json
- https://github.com/fosrl/pangolin
- https://nvd.nist.gov/vuln/detail/CVE-2026-72564
- https://github.com/fosrl/pangolin/blob/main/server/routers/resource/authWithAccessToken.ts
