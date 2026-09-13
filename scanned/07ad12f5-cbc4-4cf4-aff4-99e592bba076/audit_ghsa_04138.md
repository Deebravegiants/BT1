# [M] Claw Orchestrator is missing authentication for the component API Endpoint

## Summary
Severity: Medium
Advisory: GHSA-q6qc-xp4q-rjq5
CVE: CVE-2026-10281
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-q6qc-xp4q-rjq5
Type: github-advisory

## Affected
- npm: `@enderfga/claw-orchestrator` — affected >=0 <3.5.6

## Details
A weakness has been identified in Enderfga claw-orchestrator up to 3.5.5. This affects the function EmbeddedServer of the file src/embedded-server.ts of the component API Endpoint. This manipulation causes missing authentication. The attack may be initiated remotely. The exploit has been made available to the public and could be used for attacks. Upgrading to version 3.5.6 mitigates this issue. Patch name: d0b02a800aa0689d9428cc4cc170e0b6589fb2c3. The affected component should be upgraded.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-10281
- https://github.com/Enderfga/claw-orchestrator/issues/61
- https://github.com/Enderfga/claw-orchestrator/commit/d0b02a800aa0689d9428cc4cc170e0b6589fb2c3
- https://github.com/Enderfga/claw-orchestrator
- https://github.com/Enderfga/claw-orchestrator/releases/tag/v3.5.6
- https://vuldb.com/cve/CVE-2026-10281
- https://vuldb.com/submit/825429
- https://vuldb.com/vuln/367574
- https://vuldb.com/vuln/367574/cti
