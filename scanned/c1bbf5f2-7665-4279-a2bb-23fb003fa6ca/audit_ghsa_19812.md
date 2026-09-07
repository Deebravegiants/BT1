# [H] BentoML vulnerable to Uncontrolled Resource Consumption

## Summary
Severity: High
Advisory: GHSA-hh3j-9m59-p8vc
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-hh3j-9m59-p8vc
Type: github-advisory

## Affected
- PyPI: `bentoml` — affected >=0

## Details
In bentoml/bentoml version 1.3.9, the `/login` endpoint of the newly integrated Gradio app is vulnerable to a Denial of Service (DoS) attack. This vulnerability can be exploited by appending characters, such as dashes (-), to the end of a multipart boundary in an HTTP request. The server continuously processes each character, leading to excessive resource consumption and rendering the service unavailable. The issue is unauthenticated and does not require any user interaction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8966
- https://github.com/bentoml/BentoML
- https://huntr.com/bounties/7b5932bb-58d1-4e71-b85c-43dc40522ff2
- https://huntr.com/bounties/e467ec92-0ad1-4461-8468-1beabf701b9f
