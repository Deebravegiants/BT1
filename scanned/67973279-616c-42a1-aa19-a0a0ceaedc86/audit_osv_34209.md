# [M] Gitpod Classic Affected by Bitbucket OAuth Token Exposure via Redirect Fragment

## Summary
Severity: Medium
Advisory: CVE-2025-55750
Aliases: GHSA-63fw-3jgp-2p2g
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2025-08-29
Source: https://osv.dev/vulnerability/CVE-2025-55750
Type: osv

## Details
Gitpod is a developer platform for cloud development environments. In versions before main-gha.33628 for both Gitpod Classic and Gitpod Classic Enterprise, OAuth integration with Bitbucket in certain conditions allowed a crafted link to expose a valid Bitbucket access token via the URL fragment when clicked by an authenticated user. This resulted from how Bitbucket returned tokens and how Gitpod handled the redirect flow. The issue was limited to Bitbucket (GitHub and GitLab integrations were not affected), required user interaction, and has been mitigated through redirect handling and OAuth logic hardening. The issue was resolved in main-gha.33628 and later. There are no workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55750.json
- https://github.com/gitpod-io/gitpod/security/advisories/GHSA-63fw-3jgp-2p2g
- https://nvd.nist.gov/vuln/detail/CVE-2025-55750
- https://github.com/gitpod-io/gitpod/commit/a736c1b83bd781786af0da705d0acebabfba7862
- https://github.com/gitpod-io/gitpod/pull/20983
