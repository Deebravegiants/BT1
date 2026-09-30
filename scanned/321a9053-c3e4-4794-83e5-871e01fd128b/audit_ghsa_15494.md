# [M] Inefficient Regular Expression Complexity in langflow

## Summary
Severity: Medium
Advisory: GHSA-355v-2rjx-fpx7
CVE: CVE-2024-9277
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-09-27
Source: https://github.com/advisories/GHSA-355v-2rjx-fpx7
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0

## Details
A vulnerability classified as problematic was found in Langflow up to 1.0.18. Affected by this vulnerability is an unknown functionality of the file \src\backend\base\langflow\interface\utils.py of the component HTTP POST Request Handler. The manipulation of the argument remaining_text leads to inefficient regular expression complexity. The exploit has been disclosed to the public and may be used. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9277
- https://github.com/langflow-ai/langflow
- https://github.com/langflow-ai/langflow/blob/main/src/backend/base/langflow/interface/utils.py#L65
- https://rumbling-slice-eb0.notion.site/Remote-Redos-in-https-github-com-langflow-ai-langflow-067159ced0d5494e91b06071384969c4?pvs=4
- https://vuldb.com/?ctiid.278659
- https://vuldb.com/?id.278659
- https://vuldb.com/?submit.410043
