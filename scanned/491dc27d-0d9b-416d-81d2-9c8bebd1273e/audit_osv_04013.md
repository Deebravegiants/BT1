# [M] BIT-airflow-2020-17511

## Summary
Severity: Medium
Advisory: BIT-airflow-2020-17511
Aliases: CVE-2020-17511, GHSA-cvcq-gmc3-q6m8, PYSEC-2020-262
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-airflow-2020-17511
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <1.10.13

## Details
In Airflow versions prior to 1.10.13, when creating a user using airflow CLI, the password gets logged in plain text in the Log table in Airflow Metadatase. Same happened when creating a Connection with a password field.

## References
- https://lists.apache.org/thread.html/ree782a29d927b96bf0b39fb92e2f1f09ea3112a985f7a08ce93765ac%40%3Cusers.airflow.apache.org%3E
- https://nvd.nist.gov/vuln/detail/CVE-2020-17511
