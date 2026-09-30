# [M] Matrix-appservice-irc vulnerable to sql injection via roomIds argument

## Summary
Severity: Medium
Advisory: GHSA-ffwf-47x2-jpr8
CVE: CVE-2022-3971
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-11-13
Source: https://github.com/advisories/GHSA-ffwf-47x2-jpr8
Type: github-advisory

## Affected
- npm: `matrix-appservice-irc` — affected >=0 <0.36.0

## Details
A vulnerability was found in matrix-appservice-irc up to 0.35.1. This vulnerability affects the file src/datastore/postgres/PgDataStore.ts. The manipulation of the argument roomIds leads to sql injection. Upgrading to version 0.36.0 is able to address this issue. The name of the patch is 179313a37f06b298150edba3e2b0e5a73c1415e7. It is recommended to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3971
- https://github.com/matrix-org/matrix-appservice-irc/pull/1619
- https://github.com/matrix-org/matrix-appservice-irc/commit/179313a37f06b298150edba3e2b0e5a73c1415e7
- https://github.com/matrix-org/matrix-appservice-irc
- https://github.com/matrix-org/matrix-appservice-irc/releases/tag/0.36.0
- https://vuldb.com/?id.213550
