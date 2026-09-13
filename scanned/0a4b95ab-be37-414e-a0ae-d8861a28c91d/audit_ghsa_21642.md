# [C] Reuse of one time passwords allowed in Gitea

## Summary
Severity: Critical
Advisory: GHSA-hfmf-q69j-6m5p
CVE: CVE-2021-45331
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-hfmf-q69j-6m5p
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.5.0

## Details
An Authentication Bypass vulnerability exists in Gitea before 1.5.0, which could let a malicious user gain privileges. If captured, the TOTP code for the 2FA can be submitted correctly more than once.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45331
- https://github.com/go-gitea/gitea/pull/3878
- https://blog.gitea.io/2018/08/gitea-1.5.0-is-released
