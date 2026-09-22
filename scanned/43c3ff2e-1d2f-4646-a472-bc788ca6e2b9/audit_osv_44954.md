# [C] OS command injection in the task synthesis component in projen

## Summary
Severity: Critical
Advisory: CVE-2026-89066
Aliases: GHSA-q6g4-h6vc-vqm8
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-11
Source: https://osv.dev/vulnerability/CVE-2026-89066
Type: osv

## Details
Improper neutralization of special elements used in an OS command in the task synthesis component in projen before 0.103.0 might allow context-dependent attackers to execute arbitrary commands on a developer workstation or continuous integration runner via shell metacharacters in project configuration values and repository file names that are interpolated into generated task definitions.



To remediate this issue, users should upgrade to version 0.103.0 and then re-synthesize the project so that .projen/tasks.json is regenerated with the corrected task definitions. Upgrading alone is not sufficient because the generated task definition file is committed to the repository.

## References
- https://aws.amazon.com/security/security-bulletins/2026-108-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/89xxx/CVE-2026-89066.json
- https://github.com/projen/projen/releases/tag/v0.103.0
- https://github.com/projen/projen/security/advisories/GHSA-q6g4-h6vc-vqm8
- https://nvd.nist.gov/vuln/detail/CVE-2026-89066
