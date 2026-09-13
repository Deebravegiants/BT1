# [H] OpenChoreo: Unauthenticated Backstage developer-portal API exposes OpenChoreo catalog data, scaffolder logs, and allows unauthenticated catalog write/delete

## Summary
Severity: High
Advisory: CVE-2026-73666
Aliases: GHSA-v7qx-mqhq-grvh
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73666
Type: osv

## Details
OpenChoreo is a developer platform for Kubernetes. Prior to 1.0.4, 1.1.4, and 1.2.1, the OpenChoreo Backstage backend hardcoded backend.auth.dangerouslyDisableDefaultAuthPolicy and auth.providers.guest.dangerouslyAllowOutsideDevelopment to true, exposing /api/* without authentication and allowing unauthenticated catalog reads, scaffolder log reads, and catalog location creation or deletion. This issue is fixed in versions 1.0.4, 1.1.4, and 1.2.1.

## References
- https://github.com/openchoreo/backstage-plugins/releases/tag/v1.0.4
- https://github.com/openchoreo/backstage-plugins/releases/tag/v1.1.4
- https://github.com/openchoreo/backstage-plugins/releases/tag/v1.2.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73666.json
- https://github.com/openchoreo/openchoreo/security/advisories/GHSA-v7qx-mqhq-grvh
- https://nvd.nist.gov/vuln/detail/CVE-2026-73666
- https://github.com/openchoreo/backstage-plugins/commit/114a215689924b917da5fd28c56e679aaccaef07
- https://github.com/openchoreo/backstage-plugins/commit/dfa3fc8bd1ffef1346442c891e3e3dd54bc26501
- https://github.com/openchoreo/backstage-plugins/commit/f6df89c15834506902b2f706a9e8fbe1f6ef1474
- https://github.com/openchoreo/backstage-plugins/commit/fdaceeb737938e830c48a150d5bec24f5f487e52
- https://github.com/openchoreo/backstage-plugins/pull/709
- https://github.com/openchoreo/backstage-plugins/pull/712
- https://github.com/openchoreo/backstage-plugins/pull/713
- https://github.com/openchoreo/backstage-plugins/pull/716
