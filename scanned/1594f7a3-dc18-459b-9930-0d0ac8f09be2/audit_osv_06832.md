# [H] Denial of Service through Batched Queries in GraphQL in mlflow/mlflow

## Summary
Severity: High
Advisory: BIT-mlflow-2025-0453
Aliases: CVE-2025-0453, GHSA-49m6-vrr9-2cqm, PYSEC-2026-1637
Ecosystem: Bitnami
Published: 2025-04-03
Source: https://osv.dev/vulnerability/BIT-mlflow-2025-0453
Type: osv

## Affected
- Bitnami: `mlflow` — affected >=2.17.2 <2.18.0

## Details
In mlflow/mlflow version 2.17.2, the `/graphql` endpoint is vulnerable to a denial of service attack. An attacker can create large batches of queries that repeatedly request all runs from a given experiment. This can tie up all the workers allocated by MLFlow, rendering the application unable to respond to other requests. This vulnerability is due to uncontrolled resource consumption.

## References
- https://huntr.com/bounties/788327ec-714a-4d5c-83aa-8df04dd7612b
- https://nvd.nist.gov/vuln/detail/CVE-2025-0453
