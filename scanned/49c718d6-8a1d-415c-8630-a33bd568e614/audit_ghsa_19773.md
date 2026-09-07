# [H] Open WebUI denial of service through endpoint for converting markdown

## Summary
Severity: High
Advisory: GHSA-5v9m-57mq-qc75
CVE: CVE-2024-7983
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-5v9m-57mq-qc75
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0

## Details
In version 0.3.8 of open-webui, an endpoint for converting markdown to HTML is exposed without authentication. A maliciously crafted markdown payload can cause the server to spend excessive time converting it, leading to a denial of service. The server becomes unresponsive to other requests until the conversion is complete.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7983
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/blob/eff736acd2e0bbbdd0eeca4cc209b216a1f23b6a/backend/apps/webui/routers/utils.py#L49
- https://huntr.com/bounties/f8156ca5-1328-480f-a72b-8d3dfdad87dc
