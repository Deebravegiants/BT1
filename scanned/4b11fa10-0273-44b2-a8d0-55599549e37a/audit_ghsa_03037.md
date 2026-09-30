# [H] Prototype Pollution in Dynamoose

## Summary
Severity: High
Advisory: GHSA-rrqm-p222-8ph2
CVE: CVE-2021-21304
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-02-08
Source: https://github.com/advisories/GHSA-rrqm-p222-8ph2
Type: github-advisory

## Affected
- npm: `dynamoose` — affected >=2.0.0 <2.7.0

## Details
### Impact

In Dynamoose versions 2.0.0-2.6.0 there was a prototype pollution vulnerability in the internal utility method [`lib/utils/object/set.ts`](https://github.com/dynamoose/dynamoose/blob/master/lib/utils/object/set.ts). This method is used throughout the codebase for various operations throughout Dynamoose.

We have not seen any evidence of this vulnerability being exploited.

We do not believe this issue impacts v1.x.x since this method was added as part of the v2 rewrite. This vulnerability also impacts v2.x.x beta/alpha versions.

### Patches

v2.7.0 includes a patch for this vulnerability.

### Workarounds

We are unaware of any workarounds to patch this vulnerability other than upgrading to v2.7.0 or greater.

### References

- Patch commit hash: 324c62b4709204955931a187362f8999805b1d8e

### For more information

If you have any questions or comments about this advisory:

* [Contact me](https://charlie.fish/contact)
* [Read our Security Policy](https://github.com/dynamoose/dynamoose/blob/master/SECURITY.md)

### Credit

- GitHub CodeQL Code Scanning

## References
- https://github.com/dynamoose/dynamoose/security/advisories/GHSA-rrqm-p222-8ph2
- https://nvd.nist.gov/vuln/detail/CVE-2021-21304
- https://github.com/dynamoose/dynamoose/commit/324c62b4709204955931a187362f8999805b1d8e
- https://github.com/dynamoose/dynamoose
- https://github.com/dynamoose/dynamoose/releases/tag/v2.7.0
- https://www.npmjs.com/package/dynamoose
