# [M] OpenChoreo: Unauthenticated build/workflow trigger via git-provider confusion (webhook signature bypass)

## Summary
Severity: Medium
Advisory: CVE-2026-73840
Aliases: GHSA-c5f6-2rm9-2w8g, GO-2026-6360
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73840
Type: osv

## Details
OpenChoreo is a complete, open-source developer platform for Kubernetes. Prior to 1.0.3, 1.1.3, and 1.2.0-rc.2, the POST /api/v1alpha1/autobuild endpoint in internal/openchoreo-api/api/handlers/webhook_handler.go selected a webhook provider from caller-controlled X-Event-Key, accepted Bitbucket requests without HMAC-SHA256 in X-Hub-Signature or a configured bitbucket-secret, and allowed unauthenticated build triggers for components matched by repository URL and branch, including cross-provider triggers using attacker-supplied commit SHAs. This issue is fixed in versions 1.0.3, 1.1.3, and 1.2.0-rc.2.

## References
- https://github.com/openchoreo/openchoreo/releases/tag/v1.0.3
- https://github.com/openchoreo/openchoreo/releases/tag/v1.1.3
- https://github.com/openchoreo/openchoreo/releases/tag/v1.2.0-rc.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73840.json
- https://github.com/openchoreo/openchoreo/security/advisories/GHSA-c5f6-2rm9-2w8g
- https://nvd.nist.gov/vuln/detail/CVE-2026-73840
- https://github.com/openchoreo/openchoreo/commit/268efd9b762a3f4f72b55d9c1b13dfc55122127b
- https://github.com/openchoreo/openchoreo/commit/8af4a3fc8725fc2d8a9de9611e77278a5c48f978
- https://github.com/openchoreo/openchoreo/commit/f540553db7143141b73bb37fae02102e6f082a34
- https://github.com/openchoreo/openchoreo/pull/4239
- https://github.com/openchoreo/openchoreo/pull/4252
- https://github.com/openchoreo/openchoreo/pull/4253
