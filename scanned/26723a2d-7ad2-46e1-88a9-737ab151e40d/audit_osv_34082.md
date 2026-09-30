# [M] GitProxy bypasses approvals when pushing multiple branches

## Summary
Severity: Medium
Advisory: CVE-2025-54583
Aliases: GHSA-qr93-8wwf-22g4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N)
Published: 2025-07-30
Source: https://osv.dev/vulnerability/CVE-2025-54583
Type: osv

## Details
GitProxy is an application that stands between developers and a Git remote endpoint (e.g., github.com). Versions 1.19.1 and below allow users to push to remote repositories while bypassing policies and explicit approvals. Since checks and plugins are skipped, code containing secrets or unwanted changes could be pushed into a repository. This is fixed in version 1.19.2.

## References
- https://github.com/finos/git-proxy/releases/tag/v1.19.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54583.json
- https://github.com/finos/git-proxy/security/advisories/GHSA-qr93-8wwf-22g4
- https://nvd.nist.gov/vuln/detail/CVE-2025-54583
- https://github.com/finos/git-proxy/commit/a620a2f33c39c78e01783a274580bf822af3cc3a
- https://github.com/finos/git-proxy/commit/bd2ecb2099cba21bca3941ee4d655d2eb887b3a9
