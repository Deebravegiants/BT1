# [H] Apache Airflow Session Fixation vulnerability

## Summary
Severity: High
Advisory: GHSA-pm87-24wq-r8w9
CVE: CVE-2023-40273
CWE: CWE-384
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-23
Source: https://github.com/advisories/GHSA-pm87-24wq-r8w9
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.7.0rc2

## Details
The session fixation vulnerability allowed the authenticated user to continue accessing Airflow webserver even after the password of the user has been reset by the admin - up until the expiry of the session of the user. Other than manually cleaning the session database (for database session backend), or changing the secure_key and restarting the webserver, there were no mechanisms to force-logout the user (and all other users with that).

With this fix implemented, when using the database session backend, the existing sessions of the user are invalidated when the password of the user is reset. When using the securecookie session backend, the sessions are NOT invalidated and still require changing the secure key and restarting the webserver (and logging out all other users), but the user resetting the password is informed about it with a flash message warning displayed in the UI. Documentation is also updated explaining this behaviour.

Users of Apache Airflow are advised to upgrade to version 2.7.0 or newer to mitigate the risk associated with this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40273
- https://github.com/apache/airflow/pull/33347
- https://github.com/apache/airflow/commit/2caa186935151683076b74357daad83d2538a3f6
- https://github.com/apache/airflow/commit/f5d8201ea7935d17cecaf25fc90d4ef0ccdd627b
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2023-158.yaml
- https://lists.apache.org/thread/9rdmv8ln4y4ncbyrlmjrsj903x4l80nj
- https://www.openwall.com/lists/oss-security/2023/08/23/1
