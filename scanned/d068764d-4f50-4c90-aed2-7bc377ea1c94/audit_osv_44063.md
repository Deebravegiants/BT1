# [C] RansomLook API Key Disclosure Through /admin/apikeys HTML Source

## Summary
Severity: Critical
Advisory: CVE-2026-78555
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-78555
Type: osv

## Details
RansomLook exposed complete API keys in the HTML source of the authenticated /admin/apikeys administration page. Although the interface displayed only a shortened representation of each key, the full token was embedded in hidden form fields used by the enable/disable, private-access, and delete actions.


As a result, API credentials could be recovered by inspecting the page source or DOM. The credentials could also be unintentionally exposed through components that retain or inspect HTTP response bodies, such as debugging proxies, browser caches, monitoring systems, or other intermediaries. An attacker obtaining one of these tokens could subsequently authenticate using the privileges assigned to that key, including access to private data where the key was granted such permissions.


The patch removes API keys from subsequent page rendering and replaces them with SHA-256-derived opaque handles. Administrative actions submit only these handles, which are resolved back to the corresponding token on the server. The full API key is therefore disclosed only once, when it is initially created.

## References
- https://github.com/RansomLook/RansomLook/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78555.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78555
- https://github.com/RansomLook/RansomLook/commit/b358dfa4f40c677a47c602ebbb4473aeae349f5c
