# [H] Files or Directories Accessible to External Parties in ether/logs

## Summary
Severity: High
Advisory: GHSA-fp63-499m-hq6m
CVE: CVE-2021-32752
CWE: CWE-552
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-07-12
Source: https://github.com/advisories/GHSA-fp63-499m-hq6m
Type: github-advisory

## Affected
- Packagist: `ether/logs` — affected >=0 <3.0.4

## Details
### Impact
A vulnerability was found that allowed authenticated admin users to access any file on the server.

### Patches
The vulnerability has been fixed in 3.0.4.

### Workarounds
We recommend disabling the plugin if untrustworthy sources have admin access.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [ether/logs](https://github.com/ethercreative/logs/issues)

## References
- https://github.com/ethercreative/logs/security/advisories/GHSA-fp63-499m-hq6m
- https://nvd.nist.gov/vuln/detail/CVE-2021-32752
- https://github.com/ethercreative/logs/commit/eb225cc78b1123a10ce2784790f232d71c2066c4
- https://github.com/ethercreative/logs/releases/tag/3.0.4
