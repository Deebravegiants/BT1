# [H] Apache Airflow CNCF Kubernetes provider: JWT Token Exposure in KubernetesExecutor Command-Line Arguments

## Summary
Severity: High
Advisory: GHSA-524w-vq63-2xhf
CVE: CVE-2026-27173
CWE: CWE-538
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-524w-vq63-2xhf
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-cncf-kubernetes` — affected >=0 <10.17.0

## Details
JWT tokens that were used by workers in Kubernetes Executors have been exposed to users who had read only access to Kuberentes Pods. This could allow users with just read-only access to perform actions that were only available to running tasks via Task SDK and potentially allow to modify state of Airflow Database for tasks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-27173
- https://github.com/apache/airflow/pull/60108
- https://github.com/apache/airflow
- https://lists.apache.org/thread/pk3m2z4s2rkmc0v6gh9hnch9spc6stqw
- http://www.openwall.com/lists/oss-security/2026/05/19/35
