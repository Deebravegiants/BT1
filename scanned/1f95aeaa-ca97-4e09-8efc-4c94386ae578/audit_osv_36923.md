# [H] LORIS vulnerable to path traversal in electrophysiology_browser

## Summary
Severity: High
Advisory: CVE-2026-26985
Aliases: GHSA-g3pp-rqvq-xxhp
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-26985
Type: osv

## Details
LORIS (Longitudinal Online Research and Imaging System) is a self-hosted web application that provides data- and project-management for neuroimaging research. Starting in version 24.0.0 and prior to versions 26.0.5, 27.0.2, and 28.0.0, an authenticated user with the appropriate authorization can read configuration files on the server by exploiting a path traversal vulnerability. Some of these files contain hard-coded credentials. The vulnerability allows an attacker to read configuration files containing hard-coded credentials. The attacker could then authenticate to the database or other services if those credentials are reused. The attacker must be authenticated and have the required permissions. However, the vulnerability is easy to exploit and the application source code is public. This problem is fixed in LORIS v26.0.5 and v27.0.2 and above, and v28.0.0 and above. As a workaround, the electrophysiogy_browser in LORIS can be disabled by an administrator using the module manager.

## References
- https://github.com/aces/Loris/releases/tag/v26.0.5
- https://github.com/aces/Loris/releases/tag/v27.0.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26985.json
- https://github.com/aces/Loris/security/advisories/GHSA-g3pp-rqvq-xxhp
- https://nvd.nist.gov/vuln/detail/CVE-2026-26985
