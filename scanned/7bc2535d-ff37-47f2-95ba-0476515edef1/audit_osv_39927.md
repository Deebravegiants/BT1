# [M] TypeBot vulnerable to cross-typebot WhatsApp preview webhook resume via global `wa-preview-{phone}` session ids

## Summary
Severity: Medium
Advisory: CVE-2026-48494
Aliases: GHSA-fqf7-mmp5-j3jq
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-48494
Type: osv

## Details
TypeBot is a chatbot builder tool. In version 3.16.1, an authenticated user who has read access to any typebot can resume a WhatsApp preview webhook session that belongs to a different typebot by mixing an authorized `typebotId` and `blockId` and a foreign preview phone number tied to another preview session. The WhatsApp test-webhook handler authorizes the parent typebot first, but then resolves the preview chat session only by `wa-preview-{phone}`. As a result, an attacker can inject arbitrary webhook JSON into another workspace's WhatsApp preview session and advance its draft/unpublished flow without any access to the victim typebot. Version 3.17.0 patches the issue.

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48494.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-fqf7-mmp5-j3jq
- https://nvd.nist.gov/vuln/detail/CVE-2026-48494
- https://github.com/baptisteArno/typebot.io/commit/36a618610174fd168fb255d9c8ecc0d2cf61a192
- https://github.com/baptisteArno/typebot.io/pull/2499
