# [H] Rallly Broken Authorization: Any User Can Pause or Resume Any Poll via Poll ID Manipulation

## Summary
Severity: High
Advisory: CVE-2025-65033
Aliases: GHSA-4p93-v53r-vch3
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-11-19
Source: https://osv.dev/vulnerability/CVE-2025-65033
Type: osv

## Details
Rallly is an open-source scheduling and collaboration tool. Prior to version 4.5.4, an authorization flaw in the poll management feature allows any authenticated user to pause or resume any poll, regardless of ownership. The system only uses the public pollId to identify polls, and it does not verify whether the user performing the action is the poll owner. As a result, any user can disrupt polls created by others, leading to a loss of integrity and availability across the application. This issue has been patched in version 4.5.4.

## References
- https://github.com/lukevella/rallly/releases/tag/v4.5.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65033.json
- https://github.com/lukevella/rallly/security/advisories/GHSA-4p93-v53r-vch3
- https://nvd.nist.gov/vuln/detail/CVE-2025-65033
