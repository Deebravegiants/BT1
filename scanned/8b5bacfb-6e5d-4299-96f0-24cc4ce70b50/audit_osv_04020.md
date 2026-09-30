# [H] Format String Vulnerability

## Summary
Severity: High
Advisory: BIT-airflow-2022-40604
Aliases: CVE-2022-40604, GHSA-5rp4-749p-vx26, PYSEC-2022-279
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-airflow-2022-40604
Type: osv

## Affected
- Bitnami: `airflow` — affected >=2.3.0 <2.3.5

## Details
In Apache Airflow 2.3.0 through 2.3.4, part of a url was unnecessarily formatted, allowing for possible information extraction.

## References
- https://github.com/apache/airflow/pull/26337
- https://lists.apache.org/thread/z20x8m16fnhxdkoollv53w1ybsts687t
- https://nvd.nist.gov/vuln/detail/CVE-2022-40604
