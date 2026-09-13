# [M] Open edX Platform: SSRF in Studio Video Download Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-55421
Aliases: GHSA-fpf9-9rpr-jvrx
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-55421
Type: osv

## Details
Open edX Platform enables the authoring and delivery of online learning at any scale. Prior to commit 00b7c3c, the endpoint accepts user-supplied files[].url, performs a server-side fetch using "requests.get(url, allow_redirects=True)". The fetched bytes are then returned inside a ZIP response. This enables SSRF with response exfiltration. Redirect-following is enabled, and there is no timeout in the vulnerable fetch path. This issue has been patched via commit 00b7c3c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55421.json
- https://github.com/openedx/openedx-platform/security/advisories/GHSA-fpf9-9rpr-jvrx
- https://nvd.nist.gov/vuln/detail/CVE-2026-55421
- https://github.com/openedx/openedx-platform/commit/00b7c3ce418b487c5696b064fc5033594b045e75
- https://github.com/openedx/openedx-platform/commit/241b914a191ec24658b9cde75a7114db40a5d53a
- https://github.com/openedx/openedx-platform/commit/c9831c2c9f53b7aa9a61d80e6d91a9941ce52ec6
