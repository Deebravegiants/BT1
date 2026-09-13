# [M] Claw Orchestrator has inefficient regular expression complexity via validateRegex()

## Summary
Severity: Medium
Advisory: GHSA-95f6-rfpg-c3w8
CVE: CVE-2026-10291
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-02
Source: https://github.com/advisories/GHSA-95f6-rfpg-c3w8
Type: github-advisory

## Affected
- npm: `@enderfga/claw-orchestrator` — affected >=0 <3.7.1

## Details
A security vulnerability has been detected in Enderfga claw-orchestrator up to 3.7.0. The impacted element is the function validateRegex of the file claw-orchestrator/src/embedded-server.ts of the component Session Grep Endpoint. The manipulation of the argument body.pattern leads to inefficient regular expression complexity. The attack may be initiated remotely. Upgrading to version 3.7.1 is sufficient to resolve this issue. The identifier of the patch is 3f970a974c65a94555c25af9f2796f11315e4584. It is recommended to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-10291
- https://github.com/Enderfga/claw-orchestrator/issues/64
- https://github.com/Enderfga/claw-orchestrator/issues/64#issuecomment-4421942196
- https://github.com/Enderfga/claw-orchestrator/commit/3f970a974c65a94555c25af9f2796f11315e4584
- https://github.com/Enderfga/claw-orchestrator
- https://github.com/Enderfga/claw-orchestrator/releases/tag/v3.7.1
- https://vuldb.com/cve/CVE-2026-10291
- https://vuldb.com/submit/826222
- https://vuldb.com/vuln/367584
- https://vuldb.com/vuln/367584/cti
