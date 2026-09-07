# [H] Improper Authentication in Capsule Proxy

## Summary
Severity: High
Advisory: GHSA-9cwv-cppx-mqjm
CVE: CVE-2022-23652
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-23
Source: https://github.com/advisories/GHSA-9cwv-cppx-mqjm
Type: github-advisory

## Affected
- Go: `github.com/clastix/capsule-proxy` — affected >=0 <0.2.1

## Details
### Impact

Using a malicious `Connection` header, an attacker with a proper authentication mechanism could start a privilege escalation towards the Kubernetes API Server, being able to exploit the `cluster-admin` Role bound to `capsule-proxy`.

### Patches

Patch has been merged in the v0.2.1 release.

### Workarounds

Upgrading is mandatory.

## References
- https://github.com/clastix/capsule-proxy/security/advisories/GHSA-9cwv-cppx-mqjm
- https://nvd.nist.gov/vuln/detail/CVE-2022-23652
- https://github.com/clastix/capsule-proxy/issues/188
- https://github.com/clastix/capsule-proxy/commit/efe91f68ebf8a9e3d21491dc57da7b8a746415d8
- https://github.com/clastix/capsule-proxy
