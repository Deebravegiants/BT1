# [M] Composio Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-66r2-xm28-74w9
CVE: CVE-2024-8865
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-09-16
Source: https://github.com/advisories/GHSA-66r2-xm28-74w9
Type: github-advisory

## Affected
- PyPI: `composio-core` — affected >=0

## Details
A vulnerability was found in composiohq composio up to 0.5.8 and classified as problematic. Affected by this issue is the function path of the file composio\server\api.py. The manipulation of the argument file leads to path traversal. The exploit has been disclosed to the public and may be used. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8865
- https://github.com/ComposioHQ/composio
- https://github.com/ComposioHQ/composio/blob/v0.5.8/python/composio/server/api.py#L255
- https://rumbling-slice-eb0.notion.site/There-is-an-arbitrary-file-read-vulnerability-at-api-download-in-composiohq-composio-f0ec1ec26a5f434a97bb1ffde435a35b?pvs=4
- https://vuldb.com/?ctiid.277502
- https://vuldb.com/?id.277502
- https://vuldb.com/?submit.403206
