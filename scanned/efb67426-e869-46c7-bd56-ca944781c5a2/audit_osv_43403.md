# [H] OpenChoreo: Authenticated OS command injection via OpenChoreo Workflow Plane templates enables code execution in privileged pods

## Summary
Severity: High
Advisory: CVE-2026-73667
Aliases: GHSA-2mw5-23gm-pccq, GO-2026-6357
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73667
Type: osv

## Details
OpenChoreo is a complete, open-source developer platform for Kubernetes. Prior to 1.0.4, 1.1.4, and 1.2.0-rc.2, OpenChoreo Workflow Plane templates under samples/getting-started/workflow-templates/ interpolated developer-controlled workflow parameters into shell program text executed through sh -c instead of passing the values through container.env, allowing arbitrary commands to run in workflow pods while affected privileged Podman templates lacked hostUsers: false. This issue is fixed in versions 1.0.4, 1.1.4, and 1.2.0-rc.2.

## References
- https://github.com/openchoreo/openchoreo/releases/tag/v1.0.4
- https://github.com/openchoreo/openchoreo/releases/tag/v1.1.4
- https://github.com/openchoreo/openchoreo/releases/tag/v1.2.0-rc.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73667.json
- https://github.com/openchoreo/openchoreo/security/advisories/GHSA-2mw5-23gm-pccq
- https://nvd.nist.gov/vuln/detail/CVE-2026-73667
- https://github.com/openchoreo/openchoreo/commit/017c3c6d8b27c21d11c8c2b43da1846aa7ae73b9
- https://github.com/openchoreo/openchoreo/commit/65c081ff74618714cb0c82b5d0e0fad2c2cbc46b
- https://github.com/openchoreo/openchoreo/commit/b274127a4342e5433c5035384cef57478b5b65ed
- https://github.com/openchoreo/openchoreo/commit/fb2b659b9884eb45fa4f02b9cc7e89718a0276b7
- https://github.com/openchoreo/openchoreo/pull/4193
- https://github.com/openchoreo/openchoreo/pull/4243
- https://github.com/openchoreo/openchoreo/pull/4277
- https://github.com/openchoreo/openchoreo/pull/4297
