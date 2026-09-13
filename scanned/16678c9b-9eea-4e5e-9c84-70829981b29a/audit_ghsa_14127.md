# [C] Malware in pre-build binaries of bignum

## Summary
Severity: Critical
Advisory: GHSA-7cgc-fjv4-52x6
CWE: CWE-506
Ecosystem: npm
Published: 2023-05-24
Source: https://github.com/advisories/GHSA-7cgc-fjv4-52x6
Type: github-advisory

## Affected
- npm: `bignum` — affected >=0.12.2 <0.13.1

## Details
### Impact

bignum releases from v0.12.2 to v0.13.0 (inclusive) used node-pre-gyp to optionally download pre-built binary versions of the addon. These binaries were published on a now-expired S3 bucket which has since been claimed by a malicious third party which is now serving binaries containing malware that exfiltrates data from the user's computer.

### Patches

v0.13.1 does not use node-pre-gyp and does not have support for downloading pre-built binaries in any form, avoiding the risk of malicious downloads.

## References
- https://github.com/justmoon/node-bignum/security/advisories/GHSA-7cgc-fjv4-52x6
- https://github.com/justmoon/node-bignum/commit/57e48c3f052249725517415d83c7147e4a8c44c8
- https://github.com/justmoon/node-bignum/commit/72951c53e7c5c1ac157f04686dc12c3c393b4b08
- https://github.com/justmoon/node-bignum
