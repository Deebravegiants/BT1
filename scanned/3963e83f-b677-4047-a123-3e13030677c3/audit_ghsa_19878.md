# [H] LiteLLM Reveals Portion of API Key via a Logging File

## Summary
Severity: High
Advisory: GHSA-g5pg-73fc-hjwq
CVE: CVE-2024-9606
CWE: CWE-117
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-g5pg-73fc-hjwq
Type: github-advisory

## Affected
- PyPI: `litellm` — affected >=0 <1.44.12

## Details
In berriai/litellm before version 1.44.12, the `litellm/litellm_core_utils/litellm_logging.py` file contains a vulnerability where the API key masking code only masks the first 5 characters of the key. This results in the leakage of almost the entire API key in the logs, exposing a significant amount of the secret key. The issue affects version v1.44.9.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9606
- https://github.com/berriai/litellm/commit/9094071c4782183e84f10630e2450be3db55509a
- https://github.com/BerriAI/litellm
- https://huntr.com/bounties/4a03796f-a8d4-4293-84ef-d3959456223a
