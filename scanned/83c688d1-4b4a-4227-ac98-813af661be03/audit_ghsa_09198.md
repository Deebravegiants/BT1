# [M] Playwright Capture permits access to local files and internal network resources during page capture

## Summary
Severity: Medium
Advisory: GHSA-687h-xw6f-q2qw
CVE: CVE-2026-44439
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-687h-xw6f-q2qw
Type: github-advisory

## Affected
- PyPI: `PlaywrightCapture` — affected >=0 <1.39.6

## Details
Playwright Capture did not sufficiently restrict navigations and resource requests initiated by rendered pages. An attacker-controlled page could abuse browser-side redirection mechanisms, such as window.location.href, to make the capture process open file:// URLs or request resources hosted on private, loopback, link-local, or otherwise non-public IP addresses. In deployments where PlaywrightCapture processes untrusted URLs, this could allow a remote attacker to perform server-side request forgery against internal services or attempt to access local files from the capture environment. Depending on what capture artifacts are generated and exposed, responses from those resources could potentially be leaked through screenshots, saved page content, logs, or other capture outputs. The patch mitigates the issue by introducing request routing checks that block secondary requests to local files, non-global IP addresses, and .local domains when only_global_lookup is enabled, while still allowing the originally requested capture URL.

## References
- https://github.com/Lookyloo/PlaywrightCapture/security/advisories/GHSA-687h-xw6f-q2qw
- https://nvd.nist.gov/vuln/detail/CVE-2026-44439
- https://github.com/Lookyloo/PlaywrightCapture/commit/49e289eba756e4fbac1322c33cfd111411562405
- https://github.com/Lookyloo/PlaywrightCapture
