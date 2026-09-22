# [H] Mautic has an Authorization Bypass in API v2 Endpoints

## Summary
Severity: High
Advisory: GHSA-2jrw-c95w-h43g
CVE: CVE-2026-9808
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-2jrw-c95w-h43g
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=7.0.0 <7.1.2

## Details
### Summary
An authorization bypass vulnerability exists in the Mautic 7 API v2 endpoints (utilizing API Platform). Under certain conditions, roles configured with owner-scope restrictions (such as `viewown` or `editown`) are not properly enforced. This allows low-privilege authenticated API users to bypass ownership-logic controls and access or modify resources belonging to other users.

### Impact
Authenticated API users with limited roles can read or modify restricted resources—including reports, contacts, and companies—that they do not own and should not have access to. This bypasses structural tenant and privilege boundaries on the platform.

### Patched Versions
This security issue has been addressed in the following release:
* **7.1.2**

*Note: Mautic 6.x, 5.x, and 4.x branches are not affected by this vulnerability. For general security support regarding legacy Mautic 4 releases, please refer to the [ELTS](https://mautic.org/extended-long-term-support-elts/) page.*

### Workarounds
There are no official workarounds. To mitigate this issue without upgrading, temporarily revoke API credentials or narrow access permissions for any users whose roles rely on owner-scope permission containment.

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-2jrw-c95w-h43g
- https://nvd.nist.gov/vuln/detail/CVE-2026-9808
- https://github.com/mautic/mautic
