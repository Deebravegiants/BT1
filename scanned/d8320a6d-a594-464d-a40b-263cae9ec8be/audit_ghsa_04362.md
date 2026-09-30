# [M] Apache Airflow has no certificate validation on SMTP STARTTLS connections

## Summary
Severity: Medium
Advisory: GHSA-799x-qp47-8qwq
CVE: CVE-2026-49267
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-799x-qp47-8qwq
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=2.0.0 <3.2.2

## Details
Apache Airflow's EmailOperator and the underlying `airflow.utils.email` helpers established SMTP STARTTLS connections without verifying the remote certificate when the deployment used `[email] smtp_starttls=True` without `[email] smtp_ssl`. An attacker positioned between the worker and the configured SMTP server (network MITM — typical hostile-network attack-surface for environments where the SMTP relay sits outside the worker's trust boundary) could present a self-signed certificate, have the worker complete the STARTTLS handshake silently, and capture the SMTP AUTH credentials and message contents the worker forwarded.

This CVE covers the **core apache-airflow side** of the same root cause already covered for the SMTP provider by `CVE-2026-41016` (published 2026-04-27, covering `apache-airflow-providers-smtp`). Users who already applied the SMTP-provider fix from CVE-2026-41016 should additionally upgrade `apache-airflow` to 3.2.2 or later to cover the core-side path through `airflow.utils.email`. Affects deployments configured with `smtp_starttls=True` and `smtp_ssl=False` where the SMTP relay is reachable across a less-trusted network segment than the worker.

Users are advised to upgrade to `apache-airflow` 3.2.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-49267
- https://github.com/apache/airflow/pull/65346
- https://github.com/apache/airflow
- https://lists.apache.org/thread/6v2ds757000msmjmovnnqryqzks83ps0
