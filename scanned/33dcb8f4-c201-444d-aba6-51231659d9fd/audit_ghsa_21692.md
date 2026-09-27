# [C] Capture-replay in Gitea

## Summary
Severity: Critical
Advisory: GHSA-jrpg-35hw-m4p9
CVE: CVE-2021-45327
CWE: CWE-294
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-jrpg-35hw-m4p9
Type: github-advisory

## Affected
- Go: `github.com/go-gitea/gitea` — affected >=0 <1.11.2

## Details
Gitea is a project to help users set up a self-hosted Git service. Gitea before 1.11.2 is affected by Trusting HTTP Permission Methods on the Server Side when referencing the vulnerable admin or user API. This could allow a remote malicious user to execute arbitrary code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45327
- https://github.com/go-gitea/gitea/pull/10462
- https://github.com/go-gitea/gitea/pull/10465
- https://github.com/go-gitea/gitea/pull/10582
- https://github.com/go-gitea/gitea/commit/4cb18601ff33dda5edb47d5b452cc8f2dc39dd67
- https://github.com/go-gitea/gitea/commit/6f5656ab0ebec03fe63898208dabc802c4be46ab
- https://github.com/go-gitea/gitea/commit/ed664a9e1dae4d4660e60c981173bbc5102e69ea
- https://blog.gitea.io/2020/03/gitea-1.11.2-is-released
- https://github.com/go-gitea/gitea
