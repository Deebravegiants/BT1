# [H] Spinnaker: Improper yaml processing on kustomize bake operations

## Summary
Severity: High
Advisory: GHSA-p68j-q7hf-3qcp
CVE: CVE-2026-55175
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-p68j-q7hf-3qcp
Type: github-advisory

## Affected
- Maven: `io.spinnaker.rosco:rosco-manifests` — affected >=0 <2025.3.4
- Maven: `io.spinnaker.rosco:rosco-manifests` — affected >=2025.4.0 <2025.4.4
- Maven: `io.spinnaker.rosco:rosco-manifests` — affected >=2026.0.0 <2026.0.3
- Maven: `io.spinnaker.rosco:rosco-manifests` — affected >=2026.1.0 <2026.1.1

## Details
### Impact
Kustomize bake operations allow unsafe tag processing.  This can lead to RCE type exploits on the rosco pods when doing kustomize bakes.  This ONLY is possible when using Kustomize.  The simple solution is to block kustomize operations and instead use another provider.

### Workarounds
Disable kustomize bakes

## References
- https://github.com/spinnaker/spinnaker/security/advisories/GHSA-p68j-q7hf-3qcp
- https://nvd.nist.gov/vuln/detail/CVE-2026-55175
- https://github.com/spinnaker/spinnaker/commit/2d75818b85cc4c35144d5e5ed45e7340fcab5dfe
- https://github.com/spinnaker/spinnaker/commit/bbc30c9b9034a056e95f012fa1b34e9fd703cae7
- https://github.com/spinnaker/spinnaker/commit/de5a7a05af35aee19eb71d289cd0b77f67509009
- https://github.com/spinnaker/spinnaker/commit/df32d568e82519d9f3896fc9007baba0077c87fd
- https://github.com/spinnaker/spinnaker/commit/f5cec213f8cf207843ed5a6929395960a1ca094f
- https://github.com/spinnaker/spinnaker
- https://github.com/spinnaker/spinnaker/releases/tag/rosco-2025.3.4
- https://github.com/spinnaker/spinnaker/releases/tag/rosco-2025.4.4
- https://github.com/spinnaker/spinnaker/releases/tag/rosco-2026.0.3
- https://github.com/spinnaker/spinnaker/releases/tag/rosco-2026.1.1
- https://github.com/spinnaker/spinnaker/releases/tag/rosco-2026.2.0
