# [H] H2O Vulnerable to Denial of Service (DoS) and File Write

## Summary
Severity: High
Advisory: GHSA-wjpv-64v2-2qpq
CVE: CVE-2024-10572
CWE: CWE-400, CWE-94
Ecosystem: Maven, PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-wjpv-64v2-2qpq
Type: github-advisory

## Affected
- PyPI: `h2o` — affected >=3.34.0.1
- Maven: `ai.h2o:h2o-ext-xgboost` — affected >=3.34.0.1

## Details
In h2oai/h2o-3 version 3.46.0.1, the `run_tool` command exposes classes in the `water.tools` package through the `ast` parser. This includes the `XGBoostLibExtractTool` class, which can be exploited to shut down the server and write large files to arbitrary directories, leading to a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10572
- https://github.com/h2oai/h2o-3
- https://github.com/h2oai/h2o-3/blob/5e45e780f597961bda73adff765976db975f204b/h2o-extensions/xgboost/src/main/java/water/tools/XGBoostLibExtractTool.java#L12
- https://huntr.com/bounties/db8939a0-9be8-4d0f-a8b0-1bd181666da2
