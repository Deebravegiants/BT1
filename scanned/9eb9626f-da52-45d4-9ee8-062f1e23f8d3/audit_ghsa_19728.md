# [M] aizuda snail-job Vulnerable to Deserialization via `nodeExpression` Argument

## Summary
Severity: Medium
Advisory: GHSA-4m5h-5v4q-4xgq
CVE: CVE-2025-2622
CWE: CWE-20, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-03-22
Source: https://github.com/advisories/GHSA-4m5h-5v4q-4xgq
Type: github-advisory

## Affected
- Maven: `com.aizuda:snail-job` — affected 1.4.0

## Details
A vulnerability was found in aizuda snail-job 1.4.0. It has been classified as critical. Affected is the function getRuntime of the file /snail-job/workflow/check-node-expression of the component Workflow-Task Management Module. The manipulation of the argument nodeExpression leads to deserialization. It is possible to launch the attack remotely. The exploit has been disclosed to the public and may be used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2622
- https://gitee.com/aizuda/snail-job
- https://gitee.com/aizuda/snail-job/issues/IBSQ24
- https://gitee.com/aizuda/snail-job/issues/IBSQ24#note_38500450_link
- https://vuldb.com/?ctiid.300624
- https://vuldb.com/?id.300624
- https://vuldb.com/?submit.518999
