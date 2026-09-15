# [H] Apache Airflow Git provider: Git provider hook defaults to StrictHostKeyChecking=no, disabling SSH host-key verification

## Summary
Severity: High
Advisory: CVE-2026-58065
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-58065
Type: osv

## Details
The Apache Airflow Git provider runs its git-over-SSH operations with `StrictHostKeyChecking=no` by default, disabling SSH host-key verification. An attacker who can intercept the network path between an Airflow worker and the Git server can impersonate the server (man-in-the-middle), capturing the SSH deploy key or injecting malicious repository content. Deployments that use the Git DAG bundle or Git provider to clone over SSH with a deploy key are affected. The fix changes the default to verify host keys; upgrade to apache-airflow-providers-git `0.4.1` or later and configure a `known_hosts` file.

## References
- http://www.openwall.com/lists/oss-security/2026/07/13/3
- https://pypi.python.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58065.json
- https://lists.apache.org/thread/fjmclngfksz2kp7llpcjxzdz568h0zhc
- https://nvd.nist.gov/vuln/detail/CVE-2026-58065
- https://github.com/apache/airflow/pull/69103
