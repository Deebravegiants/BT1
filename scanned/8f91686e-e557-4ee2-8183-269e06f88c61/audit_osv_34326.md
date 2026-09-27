# [M] Outline's Local File Storage Feature can Cause CSP Bypass

## Summary
Severity: Medium
Advisory: CVE-2025-58351
Aliases: GHSA-gcj7-c9jv-fhgf
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N)
Published: 2025-09-03
Source: https://osv.dev/vulnerability/CVE-2025-58351
Type: osv

## Details
Outline is a service that allows for collaborative documentation. In versions 0.72.0 through 0.83.0, Outline introduced a feature which facilitates local file system storage capabilities as an optional file storage strategy. This feature allowed a CSP bypass as well as a ContentType bypass that might facilitate further attacks. In the case of self-hosting and using Outline FILE_STORAGE=local on the same domain as the Outline application, a malicious payload can be uploaded as a file attachment and bypass those CSP restrictions, allowing script execution within the context of another user. This is fixed in version 0.84.0.

## References
- https://github.com/outline/outline/releases/tag/v0.84.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58351.json
- https://github.com/outline/outline/security/advisories/GHSA-gcj7-c9jv-fhgf
- https://nvd.nist.gov/vuln/detail/CVE-2025-58351
- https://github.com/outline/outline/commit/18bc93c9c207329244c6909606a2393e863892a3
