# [C] OpenChoreo: cluster-gateway internal proxy performs no caller authentication and is not read-only — data-plane Secret disclosure and arbitrary Kubernetes mutation

## Summary
Severity: Critical
Advisory: CVE-2026-73842
Aliases: GHSA-rh53-xvx2-j327, GO-2026-6428
CVSS: 9.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73842
Type: osv

## Details
OpenChoreo is a complete, open-source developer platform for Kubernetes. Prior to 1.0.3, 1.1.3, and 1.2.0-rc.2, internal/cluster-gateway/server.go exposed /api/proxy/, /api/exec/, and /api/wirelogs/ on an internal listener without requiring a client certificate or token, allowing any network-reachable caller to read tenant Kubernetes Secrets, mutate workloads, and execute commands across connected data planes. This issue is fixed in versions 1.0.3, 1.1.3, and 1.2.0-rc.2.

## References
- https://github.com/openchoreo/openchoreo/releases/tag/v1.0.3
- https://github.com/openchoreo/openchoreo/releases/tag/v1.1.3
- https://github.com/openchoreo/openchoreo/releases/tag/v1.2.0-rc.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73842.json
- https://github.com/openchoreo/openchoreo/security/advisories/GHSA-rh53-xvx2-j327
- https://nvd.nist.gov/vuln/detail/CVE-2026-73842
- https://github.com/openchoreo/openchoreo/commit/50fcae3f1753fd0ac3ae655a3fc080a761c49c04
- https://github.com/openchoreo/openchoreo/commit/93e6f10953cfc249af2222ddb6730d4b0a729129
- https://github.com/openchoreo/openchoreo/commit/e3da3c63dcf0895c693cb17ce142ef95e959b62a
- https://github.com/openchoreo/openchoreo/pull/4256
- https://github.com/openchoreo/openchoreo/pull/4258
- https://github.com/openchoreo/openchoreo/pull/4259
