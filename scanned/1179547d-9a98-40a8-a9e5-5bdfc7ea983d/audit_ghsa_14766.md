# [H] Local File Inclusion in mlflow

## Summary
Severity: High
Advisory: GHSA-j46q-5pxx-8vmw
CVE: CVE-2024-2928
CWE: CWE-22, CWE-29
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-06
Source: https://github.com/advisories/GHSA-j46q-5pxx-8vmw
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <2.11.3

## Details
A Local File Inclusion (LFI) vulnerability was identified in mlflow/mlflow, specifically in version 2.9.2, which was fixed in version 2.11.3. This vulnerability arises from the application's failure to properly validate URI fragments for directory traversal sequences such as '../'. An attacker can exploit this flaw by manipulating the fragment part of the URI to read arbitrary files on the local file system, including sensitive files like '/etc/passwd'. The vulnerability is a bypass to a previous patch that only addressed similar manipulation within the URI's query string, highlighting the need for comprehensive validation of all parts of a URI to prevent LFI attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-2928
- https://github.com/mlflow/mlflow/commit/96f0b573a73d8eedd6735a2ce26e08859527be07
- https://github.com/mlflow/mlflow
- https://github.com/pypa/advisory-database/tree/main/vulns/mlflow/PYSEC-2024-242.yaml
- https://huntr.com/bounties/19bf02d7-6393-4a95-b9d0-d6d4d2d8c298
