### Title
Signature Malleability in `GetSignersEthAddress` (Go equivalent of `ecrecover`) Used for Gateway Message and JWT Signer Recovery - ([File: core/utils/eth_signatures.go])

### Summary
The reported bug describes an unused `recoverSigner()` in Solidity that used the raw `ecrecover` precompile, which is malleable, instead of OpenZeppelin's `ECDSA` library that rejects high-`s` signatures. The chainlink Go codebase has the same bug-class, but in an actively used, unprivileged-facing code path: `GetSignersEthAddress()` in `core/utils/eth_signatures.go` recovers a signer address via `crypto.SigToPub`, the Go/geth equivalent of `ecrecover`, and performs no check that `s` is in the lower half of the secp256k1 curve order (no low-`s`/malleability enforcement), unlike OpenZeppelin's `ECDSA.recover()`.

### Finding Description
`GetSignersEthAddress` only validates signature length and normalizes `v`, then calls `crypto.SigToPub`: [1](#0-0) 

There is no check equivalent to OpenZeppelin's `ECDSA` guard against `s > secp256k1n/2`, so for any valid signature `(r, s, v)` an attacker can trivially derive a second, different-looking, but equally valid signature `(r, n-s, 1-v)` that recovers to the exact same address, without needing the private key.

This function is the sole signer-recovery primitive used by:
1. `gw_common.ExtractSigner` → `Message.ExtractSigner()` in the internet-facing gateway, called from `Message.Validate()` to populate `Body.Sender` for every legacy gateway user message before it is routed to a handler: [2](#0-1) [3](#0-2) [4](#0-3) 

2. `SigningMethodEth.Verify()`, a custom JWT signing algorithm registered globally via `jwt.RegisterSigningMethod`, used to verify ETH-address-bound JWTs: [5](#0-4) 

### Impact Explanation
Because the recovered address is unaffected by which of the two malleable signature variants is submitted, the primary damage vector is not signer impersonation (the attacker still cannot forge a signature without the key), but rather any logic that treats the *raw signature bytes* (rather than the semantic message+signer) as a unique/opaque token — e.g., for deduplication, caching keys, or as an anti-replay nonce — can be defeated: an attacker who observes one valid signed gateway message or JWT can mint a bit-different but equally valid credential for the same sender/content. I could not find within the indexed code a concrete place where the *raw signature bytes* (as opposed to the message content) are used as a replay/dedup/cache key for gateway messages or JWTs, so I cannot confirm a fully realized authentication-bypass or fund-movement impact from this path alone — this is a gap in what I could verify with the available index.

### Likelihood Explanation
Exploiting the underlying malleability arithmetic requires no privileged access — any unprivileged actor sending requests to the internet-facing gateway (or presenting an ETH-signed JWT) can construct a malleable-equivalent signature once they have observed one valid signature over the same content. However, absent a confirmed sink that relies on the raw signature (or its hash) as a uniqueness key, the practical severity is limited, similar to the original report which was downgraded because the vulnerable function was unused. Here the function *is* used, but its consumers (`Message.ExtractSigner`, `SigningMethodEth.Verify`) only rely on the *recovered address*, not on the signature bytes as an identity/anti-replay token, so likelihood of a concrete exploit is currently unconfirmed rather than proven.

### Recommendation
Replace the manual `crypto.SigToPub`-based recovery in `GetSignersEthAddress` (core/utils/eth_signatures.go) with a helper that enforces canonical low-`s` signatures (reject if `s > secp256k1n/2`), analogous to OpenZeppelin's `ECDSA.recover()`. At minimum, audit every consumer of `GetSignersEthAddress`/`ExtractSigner`/`SigningMethodEth.Verify` (gateway message handling, JWT auth) to confirm none of them use the raw signature bytes as a deduplication, cache, or replay-protection key; if any do, that is the concrete exploitable sink and must be fixed to key off message content/signer instead of raw signature bytes.

### Proof of Concept
Not established with certainty. The malleability itself is trivially demonstrable (standard secp256k1 malleability transform on any valid signature), but I was unable to locate, within the indexed portion of the codebase, a definitive sink that keys replay-protection, caching, or authorization state off the raw signature bytes produced by `Message.Sign`/`SignKS` or `SigningMethodEth.Sign`. Given the strict validation rules requiring a concrete, provable authentication/authorization bypass, and given this uncertainty, I present this as a documented weakness but cannot assert a fully proven exploitable impact from the available evidence.

### Citations

**File:** core/utils/eth_signatures.go (L14-37)
```go
func GetSignersEthAddress(msg []byte, sig []byte) (recoveredAddr common.Address, err error) {
	if len(sig) != 65 {
		return recoveredAddr, errors.New("invalid signature: signature length must be 65 bytes")
	}

	// Adjust the V component of the signature in case it uses 27 or 28 instead of 0 or 1
	if sig[64] == 27 || sig[64] == 28 {
		sig[64] -= 27
	}
	if sig[64] != 0 && sig[64] != 1 {
		return recoveredAddr, errors.New("invalid signature: invalid V component")
	}

	prefixedMsg := fmt.Sprintf("%s%d%s", EthSignedMessagePrefix, len(msg), msg)
	hash := crypto.Keccak256Hash([]byte(prefixedMsg))

	sigPublicKey, err := crypto.SigToPub(hash[:], sig)
	if err != nil {
		return recoveredAddr, err
	}

	recoveredAddr = crypto.PubkeyToAddress(*sigPublicKey)
	return recoveredAddr, nil
}
```

**File:** core/services/gateway/api/message.go (L54-88)
```go
func (m *Message) Validate() error {
	if m == nil {
		return errors.New("nil message")
	}
	if len(m.Signature) != MessageSignatureHexEncodedLen {
		return errors.New("invalid hex-encoded signature length")
	}
	if len(m.Body.MessageID) == 0 || len(m.Body.MessageID) > MessageIDMaxLen {
		return errors.New("invalid message ID length")
	}
	if strings.HasSuffix(m.Body.MessageID, NullChar) {
		return errors.New("message ID ending with null bytes")
	}
	if len(m.Body.Method) == 0 || len(m.Body.Method) > MessageMethodMaxLen {
		return errors.New("invalid method name length")
	}
	if strings.HasSuffix(m.Body.Method, NullChar) {
		return errors.New("method name ending with null bytes")
	}
	if len(m.Body.DonID) == 0 || len(m.Body.DonID) > MessageDonIDMaxLen {
		return errors.New("invalid DON ID length")
	}
	if strings.HasSuffix(m.Body.DonID, NullChar) {
		return errors.New("DON ID ending with null bytes")
	}
	if len(m.Body.Receiver) != 0 && len(m.Body.Receiver) != MessageReceiverLen {
		return errors.New("invalid Receiver length")
	}
	signerBytes, err := m.ExtractSigner()
	if err != nil {
		return err
	}
	m.Body.Sender = utils.StringToHex(string(signerBytes))
	return nil
}
```

**File:** core/services/gateway/api/message.go (L124-134)
```go
func (m *Message) ExtractSigner() (signerAddress []byte, err error) {
	if m == nil {
		return nil, errors.New("nil message")
	}
	rawData := GetRawMessageBody(&m.Body)
	signatureBytes, err := hex.DecodeString(m.Signature)
	if err != nil {
		return nil, err
	}
	return gw_common.ExtractSigner(signatureBytes, rawData...)
}
```

**File:** core/services/gateway/common/utils.go (L51-57)
```go
func ExtractSigner(signature []byte, data ...[]byte) (signerAddress []byte, err error) {
	addr, err := utils.GetSignersEthAddress(flatten(data...), signature)
	if err != nil {
		return nil, err
	}
	return addr.Bytes(), nil
}
```

**File:** core/utils/jwt.go (L113-131)
```go
// Verify verifies the given signature for the given signing string using the given public key
// key is expected to be a gethcommon.Address
func (m *SigningMethodEth) Verify(signingString string, signature []byte, key any) error {
	var ethAddr gethcommon.Address
	switch k := key.(type) {
	case gethcommon.Address:
		ethAddr = k
	default:
		return jwt.ErrInvalidKeyType
	}
	recoveredAddr, err := GetSignersEthAddress([]byte(signingString), signature)
	if err != nil {
		return err
	}
	if !bytes.Equal(recoveredAddr.Bytes(), ethAddr.Bytes()) {
		return jwt.ErrSignatureInvalid
	}
	return nil
}
```
