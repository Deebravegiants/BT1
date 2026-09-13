# [H] Apache Airflow FAB provider: FAB auth manager: a DAG named "DAGs" hijacks the global all-DAGs permission (access_control privilege escalation via resource_name() collision)

## Summary
Severity: High
Advisory: CVE-2026-59245
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-59245
Type: osv

## Details
In the Apache Airflow FAB auth manager, a DAG whose `dag_id` is `DAGs` collided with the global all-DAGs permission resource name produced by `resource_name()`, so a user granted per-DAG `access_control` on that one DAG was silently granted the global all-DAGs permission (privilege escalation). The escalation triggers when a DAG named `DAGs` exists and a lower-privileged user is given per-DAG access to it, granting that user read/edit access to every DAG. Users are advised to upgrade to `apache-airflow-providers-fab` 3.7.2 or later, which disambiguates the resource-name collision.

## References
- http://www.openwall.com/lists/oss-security/2026/07/13/4
- https://pypi.python.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59245.json
- https://lists.apache.org/thread/70f37q3mwov1vm3zolrfxlzds278c78h
- https://nvd.nist.gov/vuln/detail/CVE-2026-59245
- https://github.com/apache/airflow/pull/69106
