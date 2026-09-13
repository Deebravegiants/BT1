# [H] SentinelOne impersonated via PyPI packages

## Summary
Severity: High
Advisory: GHSA-g86j-hwg9-77q5
Ecosystem: PyPI
Published: 2022-12-27
Source: https://github.com/advisories/GHSA-g86j-hwg9-77q5
Type: github-advisory

## Affected
- PyPI: `SentinelOne` — affected >=1.0.0
- PyPI: `sentinelone-sdk` — affected >=6.2.1
- PyPI: `SentineloneSDK` — affected 1.0.0
- PyPI: `Sentinelone` — affected 1.0.0
- PyPI: `SentinelOneSDK` — affected 1.0.0

## Details
In December 2022, threat actors impersonated SentinelOne by uploading fake software development kits (SDKs) onto PyPI. The SDKs contain fully functional SentinelOne clients, but the packages also contained malicious backdoors that are only executed when called on programmatically, as opposed to during installation. The packages have since been taken down from PyPI.

## References
- https://pypi.org/project/SentinelOne
- https://www.reversinglabs.com/blog/sentinelsneak-malicious-pypi-module-poses-as-security-sdk
