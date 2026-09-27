# [M] Mautic: MST-48  Server-Side Request Forgery in Asset section 

## Summary
Severity: Medium
Advisory: GHSA-mgv8-w49f-822w
CVE: CVE-2022-25777
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2024-04-12
Source: https://github.com/advisories/GHSA-mgv8-w49f-822w
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=1.0.0-beta4 <4.4.12
- Packagist: `mautic/core` — affected >=5.0.0-alpha <5.0.4

## Details
### Impact
Prior to the patched version, an authenticated user of Mautic could read system files and access the internal addresses of the application due to a Server-Side Request Forgery (SSRF) vulnerability.

### Patches
Update to 4.4.12 or 5.0.4

### Workarounds
None

### References
- https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/

If you have any questions or comments about this advisory:

Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-mgv8-w49f-822w
- https://nvd.nist.gov/vuln/detail/CVE-2022-25777
- https://github.com/mautic/mautic/commit/b4b4ab5f0613854152ceb7b5e5228acf50648fd0
- https://github.com/mautic/mautic/commit/c54befd9eaaa49e4fc10a0fe22435c09ef2821b2
- https://github.com/mautic/mautic
