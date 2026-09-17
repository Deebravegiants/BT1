# [M] Temporal does not enforce authentication and authorization for the streaming AdminService/StreamWorkflowReplicationMessages endpoint

## Summary
Severity: Medium
Advisory: GHSA-q98v-9f9w-f49q
CVE: CVE-2026-5724
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:L/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-q98v-9f9w-f49q
Type: github-advisory

## Affected
- Go: `go.temporal.io/server` — affected >=0 <1.28.4
- Go: `go.temporal.io/server` — affected >=1.29.0-135.0 <1.29.6
- Go: `go.temporal.io/server` — affected >=1.30.0-143.0 <1.30.4

## Details
The frontend gRPC server's streaming interceptor chain did not include the authorization interceptor. When a ClaimMapper and Authorizer are configured, unary RPCs enforce authentication and authorization, but the streaming AdminService/StreamWorkflowReplicationMessages endpoint accepted requests without credentials. This endpoint is registered on the same port as WorkflowService and cannot be disabled independently. An attacker with network access to the frontend port could open the replication stream without authentication. Data exfiltration is possible, but  only when a configured replication target is correctly configured and the attacker has knowledge of the cluster configuration, as the history service validates cluster IDs and peer membership before returning replication data.




Temporal Cloud is not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5724
- https://github.com/temporalio/temporal
- https://github.com/temporalio/temporal/releases/tag/v1.28.4
- https://github.com/temporalio/temporal/releases/tag/v1.29.6
- https://github.com/temporalio/temporal/releases/tag/v1.30.4
