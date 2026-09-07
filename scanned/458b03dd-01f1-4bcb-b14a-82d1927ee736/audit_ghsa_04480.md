# [H] Apache Airflow: Execution API JWT leaked via KubernetesExecutor worker command-line args

## Summary
Severity: High
Advisory: GHSA-5j6p-jrrm-6x94
CVE: CVE-2026-49298
CWE: CWE-538
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-5j6p-jrrm-6x94
Type: github-advisory

## Affected
- PyPI: `apache-airflow-core` — affected >=0 <3.2.2

## Details
A bug in Apache Airflow's KubernetesExecutor caused JWT tokens used by worker pods to authenticate against the Execution API to be passed to the worker container as command-line arguments visible in the pod spec. An authenticated UI/API user with Kubernetes read-only access to the cluster (e.g. `pods/get` in the Airflow namespace) could harvest the JWT from `kubectl describe pod` output and then call state-mutating Execution API endpoints — triggering Dag runs, clearing runs, reading or writing Variables / Connections / XComs — as if they were a running task. Affects deployments using the `KubernetesExecutor`. Users are advised to upgrade to `apache-airflow` 3.2.2 or later. This is the airflow-core half of the same vulnerability addressed by [CVE-2026-27173](https://www.cve.org/CVERecord?id=CVE-2026-27173), which shipped the apache-airflow-providers-cncf-kubernetes side of the fix. Deployments that already upgraded `apache-airflow-providers-cncf-kubernetes` to 10.17.0 or later per the CVE-2026-27173 advisory should additionally upgrade `apache-airflow` to 3.2.2 or later to close the core-side surface — the two fixes are complementary, not duplicates.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-49298
- https://github.com/apache/airflow/pull/60108
- https://github.com/apache/airflow/pull
- https://lists.apache.org/thread/wo09vrks8189dzsot39rvrx3vnx102tt
