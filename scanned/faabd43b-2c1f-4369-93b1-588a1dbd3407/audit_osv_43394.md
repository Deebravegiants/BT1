# [C] Trigger.dev: Cross-project deployment worker registration can modify another project's deployment state

## Summary
Severity: Critical
Advisory: CVE-2026-73656
Aliases: GHSA-j6vv-pq9h-f4wj
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73656
Type: osv

## Details
Trigger.dev is a platform for building and deploying fully managed AI agents and workflows. Prior to 4.5.6, POST /api/v1/deployments/:deploymentId/background-workers calls CreateDeploymentBackgroundWorkerServiceV4.call() in apps/webapp/app/v3/services/createDeploymentBackgroundWorkerV4.server.ts, where workerDeployment.findFirst() selects a deployment by friendlyId without an environmentId predicate. A caller with a valid API key for one project can submit another project's deployment identifier, link an attacker-owned background worker to the victim deployment, and move the victim deployment from BUILDING to DEPLOYING. This issue is fixed in version 4.5.6.

## References
- https://github.com/triggerdotdev/trigger.dev/releases/tag/v4.5.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73656.json
- https://github.com/triggerdotdev/trigger.dev/security/advisories/GHSA-j6vv-pq9h-f4wj
- https://nvd.nist.gov/vuln/detail/CVE-2026-73656
- https://github.com/triggerdotdev/trigger.dev/commit/34b1a181c2a1d33a53ebab88f84b05f81fea4254
- https://github.com/triggerdotdev/trigger.dev/pull/4199
