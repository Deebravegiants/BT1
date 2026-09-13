# [M] TypeBot vulnerable to cross-typebot webhook resume via unchecked `resultId` lineage allows unauthorized control of another bot's waiting session

## Summary
Severity: Medium
Advisory: CVE-2026-47704
Aliases: GHSA-h67g-6q6g-58cj
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-47704
Type: osv

## Details
TypeBot is a chatbot builder tool. Prior to version 3.17.0, an authenticated user who has read access to any typebot can resume a waiting webhook session that belongs to a different typebot by mixing an authorized `typebotId` and `blockId` and a foreign live `resultId`. The webhook resume handler authorizes the parent typebot first, but then resolves the descendant `result` only by `resultId`. As a result, an attacker can inject arbitrary webhook JSON into another typebot's suspended session and advance its execution without any access to the victim typebot. Version 3.17.0 patches the issue.

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47704.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-h67g-6q6g-58cj
- https://nvd.nist.gov/vuln/detail/CVE-2026-47704
- https://github.com/baptisteArno/typebot.io/commit/6f915c3096bd43d4a913f0f2c7a92e8463f81a86
- https://github.com/baptisteArno/typebot.io/pull/2494
