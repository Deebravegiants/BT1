# [C] OneUptime has sandbox escape in Synthetic Monitor Playwright runtime allows project members to execute arbitrary commands on Probe

## Summary
Severity: Critical
Advisory: CVE-2026-33396
Aliases: GHSA-cqpg-phpp-9jjg
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-33396
Type: osv

## Details
OneUptime is an open-source monitoring and observability platform. Prior to version 10.0.35, a low-privileged authenticated user (ProjectMember) can achieve remote command execution on the Probe container/host by abusing Synthetic Monitor Playwright script execution. Synthetic monitor code is executed in VMRunner.runCodeInNodeVM with a live Playwright page object in context. The sandbox relies on a denylist of blocked properties/methods, but it is incomplete. Specifically, _browserType and launchServer are not blocked, so attacker code can traverse `page.context().browser()._browserType.launchServer(...)` and spawn arbitrary processes. Version 10.0.35 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33396.json
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-cqpg-phpp-9jjg
- https://nvd.nist.gov/vuln/detail/CVE-2026-33396
- https://github.com/OneUptime/oneuptime/commit/e8e4ee3ff0740eb131045ab3d67453141c46178a
