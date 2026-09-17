# [M] Improper Authentication in Apache Airflow

## Summary
Severity: Medium
Advisory: GHSA-fh37-cx83-q542
CVE: CVE-2021-26697
CWE: CWE-269, CWE-287, CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-06-18
Source: https://github.com/advisories/GHSA-fh37-cx83-q542
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=2.0.0 <2.0.1rc1

## Details
The lineage endpoint of the deprecated Experimental API was not protected by authentication in Airflow 2.0.0. This allowed unauthenticated users to hit that endpoint. This is low-severity issue as the attacker needs to be aware of certain parameters to pass to that endpoint and even after can just get some metadata about a DAG and a Task. This issue only affects Apache Airflow 2.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26697
- https://github.com/apache/airflow/commit/21cedff205e7d62675949fda2aa4616d77232b76
- https://github.com/apache/airflow/commit/24a54242d56058846c7978130b3f37ca045d5142
- https://github.com/apache/airflow/commit/93957e917ff4cfb0be11aef088bd9527cf728a04
- https://github.com/advisories/GHSA-fh37-cx83-q542
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2021-3.yaml
- https://lists.apache.org/thread.html/r36111262a59219a3e2704c71e97cf84937dae5ba7a1da99499e5d8f9@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/re21fec81baea7a6d73b0b5d31efd07cc02c61f832e297f65bb19b519%40%3Cusers.airflow.apache.org%3E
- https://lists.apache.org/thread.html/re21fec81baea7a6d73b0b5d31efd07cc02c61f832e297f65bb19b519@%3Cdev.airflow.apache.org%3E
- https://lists.apache.org/thread.html/re21fec81baea7a6d73b0b5d31efd07cc02c61f832e297f65bb19b519@%3Cusers.airflow.apache.org%3E
- http://www.openwall.com/lists/oss-security/2021/02/17/2
