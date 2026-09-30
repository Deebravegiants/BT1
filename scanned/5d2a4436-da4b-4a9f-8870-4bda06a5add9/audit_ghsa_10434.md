# [M] PowerJob's GroovyEvaluator.evaluate endpoint vulnerable to code injection

## Summary
Severity: Medium
Advisory: GHSA-wpwf-v25w-54g3
CVE: CVE-2026-5739
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-wpwf-v25w-54g3
Type: github-advisory

## Affected
- Maven: `tech.powerjob:powerjob-server-starter` — affected >=5.1.0

## Details
A security flaw has been discovered in PowerJob 5.1.0/5.1.1/5.1.2. The affected element is the function GroovyEvaluator.evaluate of the file /openApi/addWorkflowNode of the component OpenAPI Endpoint. The manipulation of the argument nodeParams results in code injection. The attack can be executed remotely. The project was informed of the problem early through an issue report but has not responded yet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5739
- https://github.com/PowerJob/PowerJob/issues/1168
- https://github.com/PowerJob/PowerJob
- https://vuldb.com/submit/786936
- https://vuldb.com/vuln/355747
- https://vuldb.com/vuln/355747/cti
