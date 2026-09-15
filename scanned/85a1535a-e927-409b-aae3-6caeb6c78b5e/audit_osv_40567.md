# [C] Kestra: Unauthenticated RCE via /configs path-suffix auth-filter bypass

## Summary
Severity: Critical
Advisory: CVE-2026-53576
Aliases: GHSA-2q47-568g-9h4f
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-53576
Type: osv

## Details
Kestra is an open-source, event-driven orchestration platform. Prior to 1.0.45 and 1.3.21, the authentication filter for the REST API (@Filter("/api/v1/**")) treats any request whose path ends in /configs as the public instance-config endpoint and forwards it without a credential check. kestra addresses its resources by URL path segments that the caller chooses (/api/v1/{tenant}/flows/{namespace}, /api/v1/{tenant}/executions/{namespace}/{id}, /api/v1/{tenant}/namespaces/{namespace}/kv/{key}). An anonymous caller picks the literal configs as the final segment, and the request bypasses Basic-Auth entirely. Because the bypass reaches the flow-create and execution-trigger routes, an unauthenticated caller creates a flow containing a Shell or Process task and runs it. The task executes as root inside the kestra container. The official docker-compose.yml mounts /var/run/docker.sock, so root in the container reaches the host Docker daemon. This vulnerability is fixed in 1.0.45 and 1.3.21.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53576.json
- https://github.com/kestra-io/kestra/security/advisories/GHSA-2q47-568g-9h4f
- https://nvd.nist.gov/vuln/detail/CVE-2026-53576
