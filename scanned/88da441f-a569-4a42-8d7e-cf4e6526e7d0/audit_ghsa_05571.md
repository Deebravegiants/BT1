# [M] malcontent OCI image pull credential exfiltration via malicious registry token realm

## Summary
Severity: Medium
Advisory: GHSA-9m43-p3cx-w8j5
CVE: CVE-2026-24845
CWE: CWE-522
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-29
Source: https://github.com/advisories/GHSA-9m43-p3cx-w8j5
Type: github-advisory

## Affected
- Go: `github.com/chainguard-dev/malcontent` — affected >=0.10.0 <1.20.3

## Details
Malcontent could be made to expose Docker registry credentials if it scanned a specially crafted OCI image reference. Malcontent uses [google/go-containerregistry](https://github.com/google/go-containerregistry) for OCI image pulls, which by default uses the Docker credential keychain. A malicious registry could return a `WWW-Authenticate` header redirecting token authentication to an attacker-controlled endpoint, causing credentials to be sent to that endpoint.

**Fix:** [Default to anonymous auth for OCI pulls](https://github.com/chainguard-dev/malcontent/commit/538ed00cdc639d687a4bd1e843a2be0428a3b3e7)

**Acknowledgements**

Thank you to Oleh Konko from [1seal](https://1seal.org/) for discovering and reporting this issue.

## References
- https://github.com/chainguard-dev/malcontent/security/advisories/GHSA-9m43-p3cx-w8j5
- https://nvd.nist.gov/vuln/detail/CVE-2026-24845
- https://github.com/chainguard-dev/malcontent/commit/538ed00cdc639d687a4bd1e843a2be0428a3b3e7
- https://github.com/chainguard-dev/malcontent
