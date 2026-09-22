# [M] composio allows Server-Side Request Forgery (SSRF) in BROWSERTOOL

## Summary
Severity: Medium
Advisory: GHSA-38mg-wm59-g64x
CVE: CVE-2024-8955
CWE: CWE-643, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-38mg-wm59-g64x
Type: github-advisory

## Affected
- PyPI: `composio-core` — affected >=0

## Details
A Server-Side Request Forgery (SSRF) vulnerability exists in composiohq/composio version v0.4.4. This vulnerability allows an attacker to read the contents of any file in the system by exploiting the BROWSERTOOL_GOTO_PAGE and BROWSERTOOL_GET_PAGE_DETAILS actions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8955
- https://github.com/ComposioHQ/composio
- https://github.com/ComposioHQ/composio/blob/master/python/composio/tools/local/browsertool/actions/goto_page.py#L1
- https://huntr.com/bounties/13bc0399-2d9b-449e-95f2-6e9a7e39383d
