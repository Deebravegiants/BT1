# [C] Kubeflow Pipelines: Unauthenticated SSRF and HTTP smuggling in Kubeflow Pipelines frontend /_proxy/ route, bypasses ENABLE_AUTHZ=true

## Summary
Severity: Critical
Advisory: CVE-2026-54745
Aliases: GHSA-gqww-5pj5-8fq7
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-54745
Type: osv

## Details
Kubeflow Pipelines enables users to build and deploy portable, scalable machine learning workflows. Prior to 2.17.0, the Kubeflow Pipelines frontend exposes an unauthenticated server-side request forgery vulnerability through the /_proxy/ route in frontend/server/proxy-middleware.ts. The _routePathWithReferer() function accepts an arbitrary attacker-controlled HTTP or HTTPS target and passes its origin to createProxyMiddleware without a host allowlist or filtering for loopback, link-local, RFC1918, or cluster-local addresses. The route remains outside the authorization middleware when ENABLE_AUTHZ=true and is reachable through /apis/v1beta1/_proxy/, /apis/v2beta1/_proxy/, /pipeline/apis/v1beta1/_proxy/, and /pipeline/apis/v2beta1/_proxy/, including through a crafted Referer header. Requests can forward attacker-controlled methods, headers such as Authorization, Cookie, and X-Forwarded-For, and POST bodies to reachable internal services, while returning the upstream response to the unauthenticated client. This can expose cloud metadata credentials, Kubernetes or service APIs, and other cluster-internal endpoints to unauthorized read or modification. This issue is fixed in version 2.17.0.

## References
- https://github.com/kubeflow/pipelines/releases/tag/2.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54745.json
- https://github.com/kubeflow/pipelines/security/advisories/GHSA-gqww-5pj5-8fq7
- https://nvd.nist.gov/vuln/detail/CVE-2026-54745
- https://github.com/kubeflow/pipelines/commit/a35f97aa4c17b25572369e5022546ab4421bdbdd
- https://github.com/kubeflow/pipelines/pull/13511
