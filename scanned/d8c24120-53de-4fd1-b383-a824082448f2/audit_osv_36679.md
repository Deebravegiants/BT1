# [H] The application evaluate UNC path in workspace name

## Summary
Severity: High
Advisory: CVE-2026-25039
Aliases: GHSA-qx56-wxpm-j4m6
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-25039
Type: osv

## Details
Parsec is a cloud-based application for simple and cryptographically secure file sharing. The application does not sanitize the workspace name, creating a vulnerability if that workspace name is a UNC path. When creating mountpoint in the windows filesystem to mount the workspace of an organization, the application does not sanitize the workspace name. The cause issue if the workspace name evaluate to a UNC path since it's allowed for the name to containt `\` char. If the UNC path is invalid (or the targeted resource is not available) the application become unresponsive otherwise the system will interact with the mounted UNC path allowing the attacker to retrieve to [`NTLM`] hash.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25039.json
- https://github.com/Scille/parsec-cloud/security/advisories/GHSA-qx56-wxpm-j4m6
- https://nvd.nist.gov/vuln/detail/CVE-2026-25039
