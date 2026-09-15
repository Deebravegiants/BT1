# [M] Cleartext Storage of Sensitive Information in HMAC SHA256 Authentication

## Summary
Severity: Medium
Advisory: GHSA-v427-c49j-8w6x
CVE: CVE-2023-48707
CWE: CWE-312
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-11-23
Source: https://github.com/advisories/GHSA-v427-c49j-8w6x
Type: github-advisory

## Affected
- Packagist: `codeigniter4/shield` — affected >=0 <1.0.0-beta.8

## Details
### Impact
**secretKey**, an important key for HMAC SHA256 authentication, was stored in the database in raw form.

If a malicious person somehow had access to the data in the database, they could use the key and secretKey for HMAC SHA256 authentication to send requests impersonating that person.

### Patches
Upgrade to Shield v1.0.0-beta.8 or later.

After upgrading, all existing secret keys must be encrypted.
See https://github.com/codeigniter4/shield/blob/develop/UPGRADING.md for details.

### Workarounds
None.

### References
- https://codeigniter4.github.io/shield/references/authentication/hmac/

### For more information
If you have any questions or comments about this advisory:
* Open an issue or discussion in [codeigniter4/shield](https://github.com/codeigniter4/shield)
* Email us at [security@codeigniter.com](mailto:security@codeigniter.com)

## References
- https://github.com/codeigniter4/shield/security/advisories/GHSA-v427-c49j-8w6x
- https://nvd.nist.gov/vuln/detail/CVE-2023-48707
- https://github.com/codeigniter4/shield/commit/f77c6ae20275ac1245330a2b9a523bf7e6f6202f
- https://github.com/codeigniter4/shield
