# [M] JWX vulnerable to a denial of service attack using compressed JWE message

## Summary
Severity: Medium
Advisory: GHSA-hj3v-m684-v259
CVE: CVE-2024-28122
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2024-03-08
Source: https://github.com/advisories/GHSA-hj3v-m684-v259
Type: github-advisory

## Affected
- Go: `github.com/lestrrat-go/jwx/v2` — affected >=0 <2.0.21
- Go: `github.com/lestrrat-go/jwx` — affected >=0 <1.2.29

## Details
### Summary
This vulnerability allows an attacker with a trusted public key to cause a Denial-of-Service (DoS) condition by crafting a malicious JSON Web Encryption (JWE) token with an exceptionally high compression ratio. When this token is processed by the recipient, it results in significant memory allocation and processing time during decompression.

### Details

**The attacker needs to obtain a valid public key to compress the payload**. It needs to be valid so that the recipient can use to successfully decompress the payload. Furthermore in context JWT processing in the v2 versions, the recipient must explicitly allow JWE handling .

The attacker then crafts a message with high compression ratio, e.g. a payload with very high frequency of repeating patterns that can decompress to a much larger size.  If the payload is large enough, recipient who is decompressing the data will have to allocate a large amount of memory, which then can lead to a denial of service.

The original report includes a reference to [1], but there are some very subtle differences between this library and the aforementioned issue. The most important aspect is that the referenced issue focuses on JWT processing, whereas this library is intentionally divided into parts that comprise JOSE, i.e. JWT, JWS, JWE, JWK. In particular, v2 of this library does not attempt to handle JWT payload enveloped in a JWE message automatically (v1 attempted to do this automatically, but it was never stable).

Reflecting this subtle difference, the approach taken to mitigate this vulnerability is slightly different from the referenced issue. The referenced issue limits the size of JWT when parsing, but the fixes for this library limits the maximum size of the decompressed data when decrypting JWE messages. Therefore the fix in this library is applicable regardless of the usage context, and a limit is now imposed on the size of the message that our JWE implementation can handle.

### Proof of Concept

Modified from the original report to fit the vulnerability better:

```go
// The value below just needs to be "large enough" so that the it puts enough strain on the
// recipient's environment. The value below is a safe size on my machine to run the test
// without causing problems. When you increase the payload size, at some point the processing
// will be slow enough to virtually freeze the program or cause a memory allocation error
const payloadSize = 1 << 31

privkey, err := rsa.GenerateKey(rand.Reader, 2048)
require.NoError(t, err, `rsa.GenerateKey should succeed`)
pubkey := &privkey.PublicKey
payload := strings.Repeat("x", payloadSize)

encrypted, err := jwe.Encrypt([]byte(payload), jwe.WithKey(jwa.RSA_OAEP, pubkey), jwe.WithContentEncryption("A128CBC-HS256"), jwe.WithCompress(jwa.Deflate))
require.NoError(t, err, `jwe.Encrypt should succeed`)
_, err = jwe.Decrypt(encrypted, jwe.WithKey(jwa.RSA_OAEP, privkey)) // Will be allocating large amounts of memory
require.Error(t, err, `jwe.Decrypt should fail`)
```

###  References

[1] [CVE-2024-21319](https://github.com/AzureAD/azure-activedirectory-identitymodel-extensions-for-dotnet/security/advisories/GHSA-8g9c-28fc-mcx2)

## References
- https://github.com/lestrrat-go/jwx/security/advisories/GHSA-hj3v-m684-v259
- https://nvd.nist.gov/vuln/detail/CVE-2024-28122
- https://github.com/lestrrat-go/jwx/commit/d01027d74c7376d66037a10f4f64af9af26a7e34
- https://github.com/lestrrat-go/jwx/commit/d43f2ceb7f0c13714dfe8854d6439766e86faa76
- https://github.com/lestrrat-go/jwx
- https://github.com/lestrrat-go/jwx/releases/tag/v1.2.29
- https://github.com/lestrrat-go/jwx/releases/tag/v2.0.21
