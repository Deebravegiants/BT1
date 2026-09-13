# [H] MLflow Experiment-scoped Label Schema CRUD API authorization

## Summary
Severity: High
Advisory: BIT-mlflow-2026-13484
Aliases: CVE-2026-13484
Ecosystem: Bitnami
Published: 2026-07-08
Source: https://osv.dev/vulnerability/BIT-mlflow-2026-13484
Type: osv

## Affected
- Bitnami: `mlflow` — affected >=0 <3.13.0

## Details
A vulnerability has been found in MLflow up to 4666cffc7912ea606d592fc38d6a75e2935f65e7. The impacted element is an unknown function of the component Experiment-scoped Label Schema CRUD API. Such manipulation leads to missing authorization. It is possible to launch the attack remotely. A high complexity level is associated with this attack. The exploitability is regarded as difficult. The exploit has been disclosed to the public and may be used. A reply to the GitHub issue explains, that "[t]he labeling schema PR has not been merged yet. The auth handlers will be added before the release."

## References
- https://github.com/mlflow/mlflow/
- https://github.com/mlflow/mlflow/issues/23608
- https://github.com/mlflow/mlflow/issues/23608#issuecomment-4560963877
- https://nvd.nist.gov/vuln/detail/CVE-2026-13484
- https://vuldb.com/cve/CVE-2026-13484
- https://vuldb.com/submit/837658
- https://vuldb.com/vuln/374481
- https://vuldb.com/vuln/374481/cti
