# [H] Apache Airflow: Bad example of BashOperator shell injection via dag_run.conf

## Summary
Severity: High
Advisory: BIT-airflow-2026-30898
Aliases: CVE-2026-30898
Ecosystem: Bitnami
Published: 2026-04-21
Source: https://osv.dev/vulnerability/BIT-airflow-2026-30898
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <3.2.0

## Details
An example of BashOperator in Airflow documentation suggested a way of passing dag_run.conf in the way that could cause unsanitized user input to be used to escalate privileges of UI user to allow execute code on worker. Users should review if any of their own DAGs have adopted this incorrect advice.

## References
- http://www.openwall.com/lists/oss-security/2026/04/17/7
- https://github.com/apache/airflow/pull/64129
- https://lists.apache.org/thread/26zmhfj1t95c1hld2r14ho81nzh1bdc8
- https://nvd.nist.gov/vuln/detail/CVE-2026-30898
