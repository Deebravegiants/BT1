# [M] jose vulnerable to resource exhaustion via specifically crafted JWE with compressed plaintext

## Summary
Severity: Medium
Advisory: GHSA-hhhv-q57g-882q
CVE: CVE-2024-28176
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-03-07
Source: https://github.com/advisories/GHSA-hhhv-q57g-882q
Type: github-advisory

## Affected
- npm: `jose` — affected >=3.0.0 <4.15.5
- npm: `jose-node-cjs-runtime` — affected >=0 <4.15.5
- npm: `jose-node-esm-runtime` — affected >=0 <4.15.5
- npm: `jose` — affected >=0 <2.0.7

## Details
A vulnerability has been identified in the JSON Web Encryption (JWE) decryption interfaces, specifically related to the [support for decompressing plaintext after its decryption](https://www.rfc-editor.org/rfc/rfc7516.html#section-4.1.3). This allows an adversary to exploit specific scenarios where the compression ratio becomes exceptionally high. As a result, the length of the JWE token, which is determined by the compressed content's size, can land below application-defined limits. In such cases, other existing application level mechanisms for preventing resource exhaustion may be rendered ineffective.

Note that as per [RFC 8725](https://www.rfc-editor.org/rfc/rfc8725.html#name-avoid-compression-of-encryp) compression of data SHOULD NOT be done before encryption, because such compressed data often reveals information about the plaintext. For this reason the v5.x major version of `jose` removed support for compressed payloads entirely and is therefore NOT affected by this advisory.

### Impact

Under certain conditions it is possible to have the user's environment consume unreasonable amount of CPU time or memory during JWE Decryption operations.

### Affected users

The impact is limited only to Node.js users utilizing the JWE decryption APIs to decrypt JWEs from untrusted sources.

You are NOT affected if any of the following applies to you

- Your code uses jose version v5.x where JWE Compression is not supported anymore
- Your code runs in an environment other than Node.js (e.g. Deno, CF Workers), which is the only runtime where JWE Compression is implemented out of the box
- Your code does not use the JWE decryption APIs
- Your code only accepts JWEs produced by trusted sources

### Patches

`v2.0.7` and `v4.15.5` releases limit the decompression routine to only allow decompressing up to 250 kB of plaintext. In v4.x it is possible to further adjust this limit via the `inflateRaw` decryption option implementation. In v2.x it is possible to further adjust this limit via the `inflateRawSyncLimit` decryption option.

### Workarounds

If you cannot upgrade and do not want to support compressed JWEs you may detect and reject these tokens early by checking the token's protected header

```js
const { zip } = jose.decodeProtectedHeader(token)
if (zip !== undefined) {
  throw new Error('JWE Compression is not supported')
}
```

If you wish to continue supporting JWEs with compressed payloads in these legacy release lines you must upgrade (v1.x and v2.x to version v2.0.7, v3.x and v4.x to version v4.15.5) and review the limits put forth by the patched releases.

### For more information
If you have any questions or comments about this advisory please open a discussion in the project's [repository](https://github.com/panva/jose/discussions/new?category=q-a&title=GHSA-hhhv-q57g-882q%20advisory%20question)

## References
- https://github.com/panva/jose/security/advisories/GHSA-hhhv-q57g-882q
- https://nvd.nist.gov/vuln/detail/CVE-2024-28176
- https://github.com/panva/jose/commit/02a65794f7873cdaf12e81e80ad076fcdc4a9314
- https://github.com/panva/jose/commit/1b91d88d2f8233f3477a5f4579aa5f8057b2ee8b
- https://github.com/panva/jose
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/I6MMWFBOXJA6ZCXNVPDFJ4XMK5PVG5RG
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KXKGNCRU7OTM5AHC7YIYBNOWI742PRMY
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UG5FSEYJ3GP27FZXC5YAAMMEC5XWKJHG
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UJO2U5ACZVACNQXJ5EBRFLFW6DP5BROY
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XJDO5VSIAOGT2WP63AXAAWNRSVJCNCRH
