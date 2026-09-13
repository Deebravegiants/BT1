# [H] Headroom vulnerable to Cross-Site WebSocket Hijacking (CSWSH)

## Summary
Severity: High
Advisory: CVE-2026-71416
Aliases: GHSA-h46j-26q3-rggf
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-09-11
Source: https://osv.dev/vulnerability/CVE-2026-71416
Type: osv

## Details
Headroom compresses data before the data reaches a large language model. Prior to version 0.35.0, the Headroom WebSocket server does not validate the `Origin` header of incoming client WebSocket requests before forwarding the request to the upstream server, allowing malicious WebSocket clients to perform arbitrary LLM requests without authentication. This can be exploited by a malicious WebSocket client executed in a traditional or headless browser such as lightpanda, if the browser has access to the Headroom proxy and the OpenAI API key is stored in the `OPENAI_API_KEY` environment variable. Version 0.35.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71416.json
- https://github.com/headroomlabs-ai/headroom/releases/tag/v0.35.0
- https://github.com/headroomlabs-ai/headroom/security/advisories/GHSA-h46j-26q3-rggf
- https://nvd.nist.gov/vuln/detail/CVE-2026-71416
