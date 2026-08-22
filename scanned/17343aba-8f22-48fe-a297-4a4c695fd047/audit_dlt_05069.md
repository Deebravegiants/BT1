# [H] Signature malleability in gnark EdDSA and ECDSA due to missing scalar checks

## Summary
Severity: High
Chain: ZK
Component: Consensys/gnark
CVE: CVE-2025-57801
CWE: Improper Verification of Cryptographic Signature
Published: 2025-08-22
Source: https://github.com/Consensys/gnark/security/advisories/GHSA-95v9-hv42-pwrj
Type: github-advisory

## Details
In version before, `sig.s` used without asserting `0 ≤ S < order` in `Verify function` in [eddsa.go](https://github.com/Consensys/gnark/blob/d9a42397979b05f95f21a601fd219b06a8d60b7b/std/signature/eddsa/eddsa.go) and [ecdsa.go](https://github.com/Consensys/gnark/blob/d9a42397979b05f95f21a601fd219b06a8d60b7b/std/signature/ecdsa/ecdsa.go), which will lead to *signature malleability* vulnerability. 



### Impact

Since gnark’s native EdDSA and ECDSA circuits lack essential constraints, multiple distinct witnesses can satisfy the same public inputs. In protocols where nullifiers or anti-replay checks are derived from `(R, S)`, this enables signature malleability and may lead to double spending.



### Exploitation

```go
package main

import (
	"crypto/rand"
	"fmt"
	"math/big"

	"github.com/consensys/gnark-crypto/ecc"
	mimcHash "github.com/consensys/gnark-crypto/ecc/bn254/fr/mimc"
	eddsaCrypto "github.com/consensys/gnark-crypto/ecc/bn254/twistededwards/eddsa"

	"github.com/consensys/gnark/backend/groth16"
	"github.com/consensys/gnark/frontend"
	"github.com/consensys/gnark/frontend/cs/r1cs"
	"github.com/consensys/gnark/std/algebra/native/twistededwards"
	stdMimc "github.com/consensys/gnark/std/hash/mimc"
	stdEddsa "github.com/consensys/gnark/std/signature/eddsa"

	te "github.com/consensys/gnark-crypto/ecc/twistededwards"
)

// Circuit
type eddsaCircuit struct {
	Msg frontend.Variable  `gnark:",public"`
	Pk  stdEddsa.PublicKey `gnark:",public"`
```

_Trimmed to 38 lines — full report: https://github.com/Consensys/gnark/security/advisories/GHSA-95v9-hv42-pwrj_
