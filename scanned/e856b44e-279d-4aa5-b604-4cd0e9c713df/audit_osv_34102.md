# [M] Electron Capture is Vulnerable to TCC Bypass via Misconfigured Node Fuses (macOS)

## Summary
Severity: Medium
Advisory: CVE-2025-54871
Aliases: GHSA-8849-p3j4-jq4h
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-08-05
Source: https://osv.dev/vulnerability/CVE-2025-54871
Type: osv

## Details
Electron Capture facilitates video playback for screen-sharing and capture. In versions 2.19.1 and below, the elecap app on macOS allows local unprivileged users to bypass macOS TCC privacy protections by enabling ELECTRON_RUN_AS_NODE. This environment variable allows arbitrary Node.js code to be executed via the -e flag, which runs inside the main Electron context, inheriting any previously granted TCC entitlements (such as access to Documents, Downloads, etc.). This issue is fixed in version 2.20.0.

## References
- https://github.com/steveseguin/electroncapture/releases/tag/2.20.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54871.json
- https://github.com/steveseguin/electroncapture/security/advisories/GHSA-8849-p3j4-jq4h
- https://nvd.nist.gov/vuln/detail/CVE-2025-54871
- https://github.com/steveseguin/electroncapture/commit/3837f54e75911bb99fa45cfa138a5e401d16f531
