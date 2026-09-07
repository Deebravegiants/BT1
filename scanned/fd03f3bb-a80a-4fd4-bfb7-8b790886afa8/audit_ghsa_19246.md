# [M] Mautic segment cloning doesn't have a proper permission check

## Summary
Severity: Medium
Advisory: GHSA-vph5-ghq3-q782
CVE: CVE-2024-47055
CWE: CWE-284, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-05-28
Source: https://github.com/advisories/GHSA-vph5-ghq3-q782
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=5.0.0-alpha <5.2.6
- Packagist: `mautic/core` — affected >=6.0.0-alpha <6.0.2

## Details
### Summary
This advisory addresses a security vulnerability in Mautic related to the segment cloning functionality. This vulnerability allows any authenticated user to clone segments without proper authorization checks.

Insecure Direct Object Reference (IDOR) / Missing Authorization: A missing authorization vulnerability exists in the `cloneAction` of the segment management. This allows an authenticated user to bypass intended permission restrictions and clone segments even if they lack the necessary permissions to create new ones.

### Mitigation
Update Mautic to a version that implements proper authorization checks for the `cloneAction` within the `ListController.php`. Ensure that users attempting to clone segments possess the appropriate creation permissions.

### Workarounds
None

If you have any questions or comments about this advisory:
Email us at security@mautic.org

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-vph5-ghq3-q782
- https://nvd.nist.gov/vuln/detail/CVE-2024-47055
- https://github.com/mautic/mautic
