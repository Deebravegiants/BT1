# [M] Mautic users able to download any files from server using filemanager

## Summary
Severity: Medium
Advisory: GHSA-qpgw-2c72-4c89
CVE: CVE-2017-1000490
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-01-19
Source: https://github.com/advisories/GHSA-qpgw-2c72-4c89
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=1.0.0 <2.12.0

## Details
### Impact
Mautic versions 1.0.0 - 2.11.0 are vulnerable to allowing any authorized Mautic user session (must be logged into Mautic) to use the Filemanager to download any file from the server that the web user has access to.

### Patches
Update to 2.12.0 or later.

### Workarounds
None

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-qpgw-2c72-4c89
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000490
- https://github.com/mautic/mautic/commit/3b01786433ae15e9a23f1eb9b0d3dfdb065b6241
- https://github.com/mautic/mautic/releases/tag/2.12.0
