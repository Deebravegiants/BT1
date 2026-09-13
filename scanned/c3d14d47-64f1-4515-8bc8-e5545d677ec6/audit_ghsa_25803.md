# [H] Improper Verification of Cryptographic Signature in node-forge

## Summary
Severity: High
Advisory: GHSA-cfm4-qjh2-4765
CVE: CVE-2022-24771
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-cfm4-qjh2-4765
Type: github-advisory

## Affected
- npm: `node-forge` — affected >=0 <1.3.0

## Details
### Impact

RSA PKCS#1 v1.5 signature verification code is lenient in checking the digest algorithm structure. This can allow a crafted structure that steals padding bytes and uses unchecked portion of the PKCS#1 encoded message to forge a signature when a low public exponent is being used.

### Patches

The issue has been addressed in `node-forge` `1.3.0`.

### References

For more information, please see
["Bleichenbacher's RSA signature forgery based on implementation error"](https://mailarchive.ietf.org/arch/msg/openpgp/5rnE9ZRN1AokBVj3VqblGlP63QE/)
by Hal Finney.

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [forge](https://github.com/digitalbazaar/forge)
* Email us at [example email address](mailto:security@digitalbazaar.com)

## References
- https://github.com/digitalbazaar/forge/security/advisories/GHSA-cfm4-qjh2-4765
- https://nvd.nist.gov/vuln/detail/CVE-2022-24771
- https://github.com/digitalbazaar/forge/commit/3f0b49a0573ef1bb7af7f5673c0cfebf00424df1
- https://github.com/digitalbazaar/forge/commit/bb822c02df0b61211836472e29b9790cc541cdb2
- https://github.com/digitalbazaar/forge
