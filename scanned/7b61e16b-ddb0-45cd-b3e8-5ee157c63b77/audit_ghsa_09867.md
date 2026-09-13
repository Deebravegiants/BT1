# [M] PowerJob vulnerable to SQL injection

## Summary
Severity: Medium
Advisory: GHSA-4fp2-3xgg-jg4w
CVE: CVE-2026-5736
CWE: CWE-74, CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-4fp2-3xgg-jg4w
Type: github-advisory

## Affected
- Maven: `tech.powerjob:powerjob-server-starter` — affected >=5.1.0

## Details
A vulnerability was identified in PowerJob 5.1.0/5.1.1/5.1.2. Impacted is an unknown function of the file powerjob-server/powerjob-server-starter/src/main/java/tech/powerjob/server/web/controller/InstanceController.java of the component detailPlus Endpoint. The manipulation of the argument customQuery leads to sql injection. Remote exploitation of the attack is possible. The project was informed of the problem early through an issue report but has not responded yet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5736
- https://github.com/PowerJob/PowerJob/issues/1167
- https://github.com/PowerJob/PowerJob/pull/1166
- https://github.com/PowerJob/PowerJob
- https://vuldb.com/submit/786727
- https://vuldb.com/vuln/355746
- https://vuldb.com/vuln/355746/cti
