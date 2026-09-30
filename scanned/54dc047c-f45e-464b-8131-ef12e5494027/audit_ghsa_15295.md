# [M] Adyen APIs Library for Python timing attack vulnerability

## Summary
Severity: Medium
Advisory: GHSA-f3q4-ggfp-jv34
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-08-30
Source: https://github.com/advisories/GHSA-f3q4-ggfp-jv34
Type: github-advisory

## Affected
- PyPI: `Adyen` — affected >=2.2.0 <7.1.0

## Details
Adyen has utility methods for validating notification HMAC signatures. The `is_valid_hmac` and `is_valid_hmac_notification` methods are vulnerable to a timing attack, you should compare the hash of the HMACs instead.

## References
- https://github.com/Adyen/adyen-python-api-library/issues/168
- https://github.com/Adyen/adyen-python-api-library/pull/170
- https://github.com/Adyen/adyen-python-api-library/commit/3292133dbc00ffc4cccfb92de672a76eaa587ca5
- https://github.com/Adyen/adyen-python-api-library
- https://github.com/pypa/advisory-database/tree/main/vulns/adyen/PYSEC-2023-1.yaml
