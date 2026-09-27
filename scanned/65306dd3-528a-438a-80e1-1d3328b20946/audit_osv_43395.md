# [M] Trigger.dev: Cross-tenant payload poisoning via packet write + replay

## Summary
Severity: Medium
Advisory: CVE-2026-73657
Aliases: GHSA-jx48-qfwm-xq67
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73657
Type: osv

## Details
Trigger.dev is a platform for building and deploying fully managed AI agents and workflows. From 4.4.2 until 4.5.0-rc.4, `POST /api/v1/runs/:runParam/replay` in apps/webapp/app/routes/api.v1.runs.$runParam.replay.ts uses `prisma.taskRun.findUnique({ where: { friendlyId: runParam } })` without a runtimeEnvironmentId filter, then ReplayTaskRunService in apps/webapp/app/v3/services/replayTaskRun.server.ts replays the selected run in the victim environment. Any valid environment API key can therefore replay another tenant's run by friendlyId, consuming victim resources and repeating side effects; when `payloadType: "application/store"` is used, overrideExistingPayloadPacket() calls conditionallyImportPacket() on existingTaskRun.payload without an integrity check, so payload bytes overwritten through a separate object-store path-traversal vulnerability become attacker-controlled input to the victim task. This issue is fixed in version 4.5.0-rc.4.

## References
- https://github.com/triggerdotdev/trigger.dev/releases/tag/v4.5.0-rc.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73657.json
- https://github.com/triggerdotdev/trigger.dev/security/advisories/GHSA-jx48-qfwm-xq67
- https://nvd.nist.gov/vuln/detail/CVE-2026-73657
- https://github.com/triggerdotdev/trigger.dev/commit/e1950778e2f2007e2d432b8f8a8fc89531c51f19
- https://github.com/triggerdotdev/trigger.dev/pull/3756
