# [H] SAP Cloud SDK for AI Python has OS Command Injection when Program Objects Execution is Enabled

## Summary
Severity: High
Advisory: GHSA-xxhh-59gh-6ffx
CVE: CVE-2023-25617
CWE: CWE-74, CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-14
Source: https://github.com/advisories/GHSA-xxhh-59gh-6ffx
Type: github-advisory

## Affected
- PyPI: `sap-ai-sdk-base` — affected >=0

## Details
SAP Business Object (Adaptive Job Server) - versions 420, 430, allows remote execution of arbitrary commands on Unix, when program objects execution is enabled, to authenticated users with scheduling rights, using the BI Launchpad, Central Management Console or a custom application based on the public java SDK. Programs could impact the confidentiality, integrity and availability of the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-25617
- https://github.com/pypa/advisory-database/tree/main/vulns/sap-ai-sdk-base/PYSEC-2023-315.yaml
- https://launchpad.support.sap.com/#/notes/3283438
- https://www.sap.com/documents/2022/02/fa865ea4-167e-0010-bca6-c68f7e60039b.html
- https://www.sap.com/index.html
