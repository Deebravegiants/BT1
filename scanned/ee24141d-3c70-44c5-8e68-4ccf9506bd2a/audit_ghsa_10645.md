# [M] mcp-url-downloader has a Server-Side Request Forgery issue

## Summary
Severity: Medium
Advisory: GHSA-h7xc-4mv8-59fj
CVE: CVE-2026-7158
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-27
Source: https://github.com/advisories/GHSA-h7xc-4mv8-59fj
Type: github-advisory

## Affected
- PyPI: `mcp-url-downloader` — affected >=0

## Details
A vulnerability has been found in dmitryglhf mcp-url-downloader up to 4b8cf2de55f6e8864a77d108e8a94a5b8e4394c6. Affected by this issue is the function _validate_url_safe of the file src/mcp_url_downloader/server.py. Such manipulation of the argument url leads to server-side request forgery. The attack can be executed remotely. The exploit has been disclosed to the public and may be used. This product implements a rolling release for ongoing delivery, which means version information for affected or updated releases is unavailable. The project was informed of the problem early through an issue report but has not responded yet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7158
- https://github.com/dmitryglhf/url-download-mcp/issues/2
- https://github.com/dmitryglhf/url-download-mcp
- https://vuldb.com/submit/802062
- https://vuldb.com/vuln/359757
- https://vuldb.com/vuln/359757/cti
