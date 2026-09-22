# [C] Apache Airflow SFTP provider: Path traversal in SFTPHook.retrieve_directory

## Summary
Severity: Critical
Advisory: GHSA-qf38-jq28-3ccq
CVE: CVE-2026-50203
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-qf38-jq28-3ccq
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-sftp` — affected >=0 <5.8.1

## Details
A path traversal in the SFTP provider (`SFTPHook.retrieve_directory` / `SFTPOperator(operation=get)`) let a malicious or compromised remote SFTP server write files outside the configured local destination directory via crafted directory-entry names. No Airflow account is required — the attack surface is any deployment downloading directories from an untrusted SFTP server. Upgrade `apache-airflow-providers-sftp` to 5.8.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50203
- https://github.com/apache/airflow/pull/67985
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow-providers-sftp/PYSEC-2026-218.yaml
- https://lists.apache.org/thread/7f4b284oh44c1n95oq8mh1qc7y1lr9dx
- http://www.openwall.com/lists/oss-security/2026/06/16/3
