# [M] Cross-Capture Session Data Leakage Due to Shared Mutable State in Looklyloo - PlaywrightCapture

## Summary
Severity: Medium
Advisory: CVE-2026-63175
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-63175
Type: osv

## Details
PlaywrightCapture stored capture-specific configuration and runtime data as mutable class-level variables rather than instance-level variables. Consequently, multiple Capture objects running within the same Python process could share state, including HTTP headers, cookies, browser storage, HTTP credentials, proxy configuration, user-agent settings, geolocation information, and captured request data.

In a multi-user or concurrent deployment, information supplied during one capture could therefore persist and be reused by a subsequent or parallel capture. This could result in the disclosure of authentication cookies, credentials, browser storage, or captured request data belonging to another user. It could also cause requests to be performed with another capture's authentication context, headers, or proxy configuration, potentially enabling unauthorized access to remote resources or interference with other capture operations.

The vulnerability is resolved by initializing all capture-specific settings and request data as instance variables in the Capture constructor, ensuring that state is isolated between capture operations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63175.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63175
- https://github.com/Lookyloo/PlaywrightCapture/commit/1e354b9d8566f49dbb331410be24c7c295645d43
- https://github.com/Lookyloo/PlaywrightCapture
