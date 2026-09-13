# [H] Apache Airflow FTP provider: FTP Provider does not protect FTPS data channel (missing PROT_P)

## Summary
Severity: High
Advisory: CVE-2026-49486
Aliases: GHSA-fgch-86x8-fv43, PYSEC-2026-238
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-49486
Type: osv

## Details
The Apache Airflow FTP provider's `FTPSHook.get_conn()` created an `ftplib.FTP_TLS` connection but never called `prot_p()`, so although the control channel was TLS-protected the data channel was transmitted in cleartext. Any deployment using `FTPSHook` or `FTPSFileTransmitOperator` to move files over FTPS exposed file contents and credentials-in-transit to a network attacker able to observe the data connection. Upgrade apache-airflow-providers-ftp to `3.15.1` or later, which issues `PROT P` to encrypt the data channel.

## References
- http://www.openwall.com/lists/oss-security/2026/06/26/1
- https://pypi.python.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49486.json
- https://lists.apache.org/thread/gwnsxlt9hfj5pc543wxtogbnjdn04xj1
- https://nvd.nist.gov/vuln/detail/CVE-2026-49486
- https://github.com/apache/airflow/pull/67946
