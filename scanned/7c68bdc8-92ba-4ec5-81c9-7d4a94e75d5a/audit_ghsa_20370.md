# [M] Exposure of Sensitive Information to an Unauthorized Actor in semantic-release

## Summary
Severity: Medium
Advisory: GHSA-x2pg-mjhr-2m5x
CVE: CVE-2022-31051
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-06-09
Source: https://github.com/advisories/GHSA-x2pg-mjhr-2m5x
Type: github-advisory

## Affected
- npm: `semantic-release` — affected >=17.0.4 <19.0.3

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

Secrets that would normally be masked by semantic-release can be accidentally disclosed if they contain characters that are excluded from uri encoding by [encodeURI](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/encodeURI). Occurrence is further limited to execution contexts where push access to the related repository is not available without modifying the repository url to inject credentials.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Fixed in 19.0.3

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

Secrets that do not contain characters that are excluded from encoding with `encodeURI` when included in a URL are already masked properly.

### References
_Are there any links users can visit to find out more?_
* https://github.com/semantic-release/semantic-release/releases/tag/v19.0.3
* https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/encodeURI

### For more information
If you have any questions or comments about this advisory:
* Open a discussion in [semantic-release discussions](https://github.com/semantic-release/semantic-release/discussions)

## References
- https://github.com/semantic-release/semantic-release/security/advisories/GHSA-x2pg-mjhr-2m5x
- https://nvd.nist.gov/vuln/detail/CVE-2022-31051
- https://github.com/semantic-release/semantic-release/pull/2449
- https://github.com/semantic-release/semantic-release/pull/2459
- https://github.com/semantic-release/semantic-release/commit/58a226f29c04ee56bbb02cc661f020d568849cad
- https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/encodeURI
- https://github.com/semantic-release/semantic-release
- https://github.com/semantic-release/semantic-release/releases/tag/v19.0.3
