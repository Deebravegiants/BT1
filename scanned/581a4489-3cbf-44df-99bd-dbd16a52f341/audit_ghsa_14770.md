# [C] litellm vulnerable to remote code execution based on using eval unsafely

## Summary
Severity: Critical
Advisory: GHSA-gppg-gqw8-wh9g
CVE: CVE-2024-5751
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-27
Source: https://github.com/advisories/GHSA-gppg-gqw8-wh9g
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=0 <1.40.16

## Details
BerriAI/litellm version v1.35.8 contains a vulnerability where an attacker can achieve remote code execution. The vulnerability exists in the `add_deployment` function, which decodes and decrypts environment variables from base64 and assigns them to `os.environ`. An attacker can exploit this by sending a malicious payload to the `/config/update` endpoint, which is then processed and executed by the server when the `get_secret` function is triggered. This requires the server to use Google KMS and a database to store a model.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-5751
- https://github.com/BerriAI/litellm/pull/4228
- https://github.com/BerriAI/litellm/commit/fcea4c22ad96b24436f196ae709f71932e84b0b8
- https://github.com/berriai/litellm
- https://huntr.com/bounties/ae623c2f-b64b-4245-9ed4-f13a0a5824ce
