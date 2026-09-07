# [H] Gogs vulnerable to Stored XSS via Mermaid diagrams

## Summary
Severity: High
Advisory: GHSA-26gq-grmh-6xm6
CWE: CWE-1395, CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-26gq-grmh-6xm6
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.13.4

## Details
### Summary
Stored XSS via mermaid diagrams due to usage of vulnerable renderer library

### Details
Gogs introduced support for rendering mermaid diagrams in version [0.13.0.](https://github.com/gogs/gogs/releases/tag/v0.13.0)

Currently used version of the library [mermaid 11.9.0](https://github.com/gogs/gogs/tree/main/public/plugins/mermaid-11.9.0) is vulnerable to at least two XSS scenarios with publicly available payloads

Resources:
https://github.com/mermaid-js/mermaid/security/advisories/GHSA-7rqq-prvp-x9jh
https://github.com/mermaid-js/mermaid/security/advisories/GHSA-8gwm-58g9-j8pw

### PoC

1. Create a markdown file eg. `README.md` containing following malicious mermaid diagram (payload based on [CVE-2025-54880](https://github.com/mermaid-js/mermaid/security/advisories/GHSA-8gwm-58g9-j8pw))
```
architecture-beta
    group api(cloud)[API]
    service db "<img src=x onerror=\"alert(document.domain)\">" [Database] in api
```
2. The XSS should pop whenever either repository or file is viewed

#### Demo

https://github.com/user-attachments/assets/98320f62-6c1c-4254-aa61-95598c725235

### Impact
The attacker can potentially achieve account takeover
In a worst case scenario if the victim were an instance admin this could lead to a compromise of the entire deployment

### Proposed remediation steps
1. Upgrade to a patched version of the third party library
https://github.com/mermaid-js/mermaid/releases/tag/v10.9.5
2. Consider running mermaid using `sandbox` level which would mitigate impact of future potential cross-site scripting issues
https://mermaid.js.org/config/usage.html#securitylevel

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-26gq-grmh-6xm6
- https://github.com/mermaid-js/mermaid/security/advisories/GHSA-7rqq-prvp-x9jh
- https://github.com/mermaid-js/mermaid/security/advisories/GHSA-8gwm-58g9-j8pw
- https://github.com/gogs/gogs/commit/71a72a72ad1c8cea7940c9d7e4cbdfbc0fc3d401
- https://github.com/gogs/gogs
