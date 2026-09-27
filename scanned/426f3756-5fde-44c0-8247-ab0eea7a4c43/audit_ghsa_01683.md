# [C] Exposure of Sensitive Information to an Unauthorized Actor in AEgir

## Summary
Severity: Critical
Advisory: GHSA-qfcv-5whw-7pcw
CVE: CVE-2020-11059
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2020-05-27
Source: https://github.com/advisories/GHSA-qfcv-5whw-7pcw
Type: github-advisory

## Affected
- npm: `aegir` — affected >=21.7.0 <21.10.1

## Details
### Impact
`aegir publish` and `aegir build` may leak secrets from environmental variables in the browser bundle published to npm.

### Patches
The code has been patched, users should upgrade to >= 21.10.1

### Workarounds
Run `printenv` to check your environment variables and revoke any secrets.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [aegir](https://github.com/ipfs/aegir)

## References
- https://github.com/ipfs/aegir/security/advisories/GHSA-qfcv-5whw-7pcw
- https://nvd.nist.gov/vuln/detail/CVE-2020-11059
- https://github.com/ipfs/aegir/commit/e36e1def57b2dc1e4b7a5beba964c5924e87f8d8
- https://github.com/ipfs/aegir
