# [H] InvokeAI has Denial of Service (DoS) vulnerability in `/api/v1/images/upload`

## Summary
Severity: High
Advisory: GHSA-6f6x-f56q-5xgv
CVE: CVE-2024-10821
CWE: CWE-400, CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-6f6x-f56q-5xgv
Type: github-advisory

## Affected
- PyPI: `InvokeAI` — affected >=0

## Details
A Denial of Service (DoS) vulnerability in the multipart request boundary processing mechanism of the Invoke-AI server (version v5.0.1) allows unauthenticated attackers to cause excessive resource consumption. The server fails to handle excessive characters appended to the end of multipart boundaries, leading to an infinite loop and a complete denial of service for all users. The affected endpoint is `/api/v1/images/upload`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10821
- https://github.com/invoke-ai/InvokeAI
- https://github.com/invoke-ai/InvokeAI/blob/807f458f13e7693ada2fb929c2d513950611fe9c/invokeai/app/api/routers/images.py#L29
- https://huntr.com/bounties/0ac24835-c4c0-4f11-938a-d5641dfb80b2
