# [C] Two LiteLLM versions published containing credential harvesting malware

## Summary
Severity: Critical
Advisory: GHSA-5mg7-485q-xm76
CWE: CWE-506
Ecosystem: PyPI
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-5mg7-485q-xm76
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=1.82.7

## Details
After an API Token exposure from an exploited trivy dependency, two new releases of `litellm` were uploaded to PyPI containing automatically activated malware, harvesting sensitive credentials and files, and exfiltrating to a remote API.

Anyone who has installed and run the project should assume any credentials available to litellm environment may have been exposed, and revoke/rotate thema ccordingly.

## References
- https://github.com/BerriAI/litellm/issues/24518
- https://docs.litellm.ai/blog/security-update-march-2026
- https://futuresearch.ai/blog/litellm-pypi-supply-chain-attack
- https://github.com/BerriAI/litellm
- https://github.com/pypa/advisory-database/tree/main/vulns/litellm/PYSEC-2026-2.yaml
- https://inspector.pypi.io/project/litellm/1.82.7/packages/79/5f/b6998d42c6ccd32d36e12661f2734602e72a576d52a51f4245aef0b20b4d/litellm-1.82.7-py3-none-any.whl/litellm/proxy/proxy_server.py#line.130
- https://inspector.pypi.io/project/litellm/1.82.8/packages/f6/2c/731b614e6cee0bca1e010a36fd381fba69ee836fe3cb6753ba23ef2b9601/litellm-1.82.8.tar.gz/litellm-1.82.8/litellm_init.pth#line.1
- https://www.wiz.io/blog/teampcp-attack-kics-github-action
