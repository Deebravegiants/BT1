# [M] MLflow Uncontrolled Resource Consumption vulnerability

## Summary
Severity: Medium
Advisory: GHSA-q3gw-8236-5jw4
CVE: CVE-2024-6838
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-q3gw-8236-5jw4
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0

## Details
In mlflow/mlflow version v2.13.2, a vulnerability exists that allows the creation or renaming of an experiment with a large number of integers in its name due to the lack of a limit on the experiment name. This can cause the MLflow UI panel to become unresponsive, leading to a potential denial of service. Additionally, there is no character limit in the `artifact_location` parameter while creating the experiment.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6838
- https://github.com/mlflow/mlflow
- https://huntr.com/bounties/8ad52cb2-2cda-4eb0-aec9-586060ee43e0
