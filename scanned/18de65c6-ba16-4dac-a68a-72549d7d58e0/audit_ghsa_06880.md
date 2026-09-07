# [H] Style Dictionary - Prototype Pollution in convertTokenData utility function

## Summary
Severity: High
Advisory: GHSA-vj5c-m527-mpff
CVE: CVE-2026-54639
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-vj5c-m527-mpff
Type: github-advisory

## Affected
- npm: `style-dictionary` — affected >=4.3.0 <5.4.4

## Details
### Impact
Prototype pollution.
A malicious user can create a token array `[{ key: '{__proto__.foo}', value: 'malicious' }]`, when processed by `convertTokenData()` utility function, it will pollute the Object.prototype globally where `{}.foo` will equal `{ key: '{__proto__.foo}', value: 'malicious' }`.

This has been confirmed with a test/reproduction.

You are impacted when:
- direct usage of `convertTokenData(tokens, { output: 'object' });`
- indirect usage, via using Expand API https://styledictionary.com/reference/config/#expand. If your expand config deems it necessary to run expand (this means, if NOT:  1) set to false, 2) all subprops set to false, or 3) undefined), then we sync the `sd.tokens` property with the `sd.tokenMap` property by converting tokenData map back to object.
- indirect usage via SD's transform lifecycle. Once your tokens are transformed, we also have to sync the `sd.tokens` property with the `sd.tokenMap` property.

Impact is high for this when style-dictionary is used as an integration in a NodeJS server application.
Impact is moderate for when style-dictionary is used as an integration in a Web application.
Impact is low for most common cases where the user of style-dictionary also maintains the tokens, and access is limited via read/write access to the repository/workflows where it is used.

### Patches
A patch has been published: version `5.4.4`.
Any version within range `>=4.3.0 <5.4.4` contains this vulnerability, see commit hash 209085d for when the vulnerability was added.

See PR with repro + fix https://github.com/style-dictionary/style-dictionary/pull/1702

### Workarounds
A workaround is to sanitize your token data first. Whether using DTCG format or old Style Dictionary format, you have to check the token data object recursively for any object keys that include `__proto__`.

You can do this with the StyleDictionary instance too, just ensure that expand has to be set to false to prevent the second method of this vulnerability from happening.

```js
const sd = new StyleDictionary({ expand: false });

if (sd.allTokens.some(tok => tok.key.includes('__proto__')) {
  throw new Error('Found malicious token key, attempting to do prototype pollution.')
}
```

## References
- https://github.com/style-dictionary/style-dictionary/security/advisories/GHSA-vj5c-m527-mpff
- https://nvd.nist.gov/vuln/detail/CVE-2026-54639
- https://github.com/style-dictionary/style-dictionary/pull/1702
- https://github.com/style-dictionary/style-dictionary/commit/209085d9782cfc0783c4d983f3f1bb2c515954ec
- https://github.com/style-dictionary/style-dictionary/commit/23b5e8dda143441f0d6b8e2b4222e2da98058bc5
- https://github.com/style-dictionary/style-dictionary
- https://github.com/style-dictionary/style-dictionary/releases/tag/v5.4.4
