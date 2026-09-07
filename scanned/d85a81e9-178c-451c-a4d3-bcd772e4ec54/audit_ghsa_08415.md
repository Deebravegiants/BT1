# [M] Prefect Unauthenticated Event Injection via /api/events/in WebSocket

## Summary
Severity: Medium
Advisory: GHSA-hvph-5985-r63v
CVE: CVE-2026-7723
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-hvph-5985-r63v
Type: github-advisory

## Affected
- PyPI: `prefect` — affected >=0 <3.6.14

## Details
A flaw has been found in PrefectHQ prefect up to 3.6.13. Affected is an unknown function of the file /api/events/in of the component WebSocket Endpoint. Executing a manipulation can lead to missing authentication. The attack may be performed from remote. The exploit has been published and may be used. Upgrading to version 3.6.14 is able to address this issue. This patch is called 0d3ab3c2d3f9f98abfafdf7b9f6d4f8ed3925e40. It is recommended to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7723
- https://github.com/PrefectHQ/prefect/pull/20372
- https://github.com/PrefectHQ/prefect/commit/0d3ab3c2d3f9f98abfafdf7b9f6d4f8ed3925e40
- https://github.com/PrefectHQ/prefect/commit/f8afecadf88ea5f73694dafa3a365b9d8fae1ad6
- https://gist.github.com/nedlir/f1ab8aa038aafbcc6beeef21fab1d74f
- https://github.com/PrefectHQ/prefect
- https://github.com/PrefectHQ/prefect/releases/tag/3.6.14
- https://vuldb.com/submit/807256
- https://vuldb.com/vuln/360899
- https://vuldb.com/vuln/360899/cti
