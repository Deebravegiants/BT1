# [H] Server-Side Request Forgery (SSRF) in GitLab AI Gateway

## Summary
Severity: High
Advisory: CVE-2026-75871
CVSS: 8.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-75871
Type: osv

## Details
GitLab has remediated a vulnerability in the GitLab AI Gateway component affecting all versions of the AI Gateway from 18.10 to 19.0.12, 19.1 to 19.1.7, and 19.2 to 19.2.2 that could have allowed an authenticated user with Duo Agent Platform access to redirect outbound model requests to an externally-controlled endpoint via a crafted inline flow configuration that overrides the HTTP Host header, resulting in disclosure of Google Cloud Vertex cloud service credentials and private signing keys.

## References
- https://gitlab.com/gitlab-org/gitlab/-/work_items/616990
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75871.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75871
- https://hackerone.com/reports/3945100
