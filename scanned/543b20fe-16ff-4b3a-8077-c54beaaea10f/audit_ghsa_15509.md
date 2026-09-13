# [H] MindsDB Deserialization of Untrusted Data vulnerability

## Summary
Severity: High
Advisory: GHSA-q9r8-89xr-4xv4
CVE: CVE-2024-45853
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-12
Source: https://github.com/advisories/GHSA-q9r8-89xr-4xv4
Type: github-advisory

## Affected
- PyPI: `mindsdb` — affected >=23.10.2.0

## Details
Deserialization of untrusted data can occur in versions 23.10.2.0 and newer of the MindsDB platform, enabling a maliciously uploaded ‘inhouse’ model to run arbitrary code on the server when used for a prediction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45853
- https://github.com/mindsdb/mindsdb
- https://github.com/mindsdb/mindsdb/blob/v24.9.2.1/mindsdb/integrations/handlers/byom_handler/byom_handler.py#L424-L431
- https://github.com/pypa/advisory-database/tree/main/vulns/mindsdb/PYSEC-2024-83.yaml
- https://hiddenlayer.com/sai-security-advisory/2024-09-mindsdb
