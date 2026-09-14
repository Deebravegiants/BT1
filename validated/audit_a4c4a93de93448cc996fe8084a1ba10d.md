### Title
Missing degenerate/all-zero public-key check in vault decryption-share encryption enables predictable-key disclosure of `tdh2easy` decryption shares - ([File: core/services/ocr2/plugins/vault/plugin.go])

### Summary
The vault OCR reporting plugin encrypts per-request TDH2 decryption shares to a caller-supplied X25519 public key via `box.SealAnonymous` in `encryptWithKeyBinary`, but only validates the key's byte length — never rejecting degenerate curve points (e.g., the all-zero point / identity element). This mirrors the `sodiumoxide` `scalarmult()` bug class (CVE-2017-1000168 / CWE-1240): an unprivileged caller can force ECDH to a fixed, non-secret shared value, defeating the confidentiality guarantee that only a holder of the matching private key can decrypt the resulting ciphertext.

### Finding Description
`share.encryptWithKeyBinary` takes an attacker-supplied hex string from `vaultcommon.SecretRequest.EncryptionKeys` (part of a `GetSecretsRequest` that reaches the OCR3 vault reporting plugin through the gateway) and uses it directly as the X25519 public key for `box.SealAnonymous`: [1](#0-0) 

The only check performed is on the decoded byte length (`len(publicKey) != curve25519.PointSize`): [2](#0-1) 

There is no check that the supplied 32-byte value is a valid, non-degenerate curve point (e.g., all-zero bytes, the identity element, or other known low-order points). `box.SealAnonymous` internally performs an X25519 scalar multiplication between a freshly generated ephemeral private key and this caller-controlled public key to derive the symmetric encryption key for the payload. When the supplied point is degenerate (e.g., all-zero), the X25519 scalar-multiplication result collapses to a fixed value independent of the ephemeral private key the node randomly generated for that call — exactly the class of bug fixed upstream by rejecting all-zero public keys in `scalarmult()`.

This function is called once per key in `secretRequest.EncryptionKeys` inside `observeGetSecretsRequest`, which is reachable by any client whose `GetSecretsRequest` passes `validateGetSecretsRequestItem` — that function only validates the secret identifier and duplicate-request checks, never the `EncryptionKeys` values themselves: [3](#0-2) [4](#0-3) 

### Impact Explanation
The encrypted decryption shares are placed into OCR `Observation`s and, per the plugin's own comments, are broadcast as blobs during the observation phase for latency reasons: [5](#0-4) 

Because these observations/blobs are gossiped among DON nodes as part of normal consensus, an attacker who submits a `GetSecretsRequest` with a degenerate `EncryptionKeys` entry causes the node(s) to encrypt sensitive `tdh2easy.DecryptionShare` material with a symmetric key that is fixed/predictable rather than bound to any private key the requester (or anyone) actually possesses. This breaks the intended cryptographic guarantee that only the holder of the corresponding private key can decrypt the share, exposing decryption-share material to any party able to observe the encrypted payload in transit or in logs — a concrete key/secret-disclosure weakness, consistent with CWE-1240.

### Likelihood Explanation
`EncryptionKeys` is fully attacker-controlled input on an unprivileged, internet-facing request path (`GetSecretsRequest` submitted through the gateway to the vault capability), and no code path in `request_validation.go` or `plugin.go` rejects degenerate values before they reach `box.SealAnonymous`. Constructing the trivial all-zero 32-byte key requires no special access.

### Recommendation
Reject degenerate/low-order public keys before calling `box.SealAnonymous` in `encryptWithKeyBinary` — at minimum reject the all-zero point, and ideally validate against the full set of known low-order Curve25519 points (as `sodiumoxide`/libsodium do), returning a `vaulttypes.NewUserError` for invalid keys just as is already done for incorrect length.

### Proof of Concept
1. Submit a `vaultcommon.GetSecretsRequest` for a secret the caller is otherwise entitled to request, with `EncryptionKeys: []string{"0000000000000000000000000000000000000000000000000000000000000000000000000000"}` (32 zero bytes hex-encoded, i.e., the curve25519 identity point).
2. `encryptWithKeyBinary` accepts the key (length check passes) and calls `box.SealAnonymous(nil, shareBytes, &zeroPublicKey, rand.Reader)`.
3. The X25519 ECDH computed inside `box.SealAnonymous` between the node's ephemeral private key and the all-zero public key yields a fixed shared secret regardless of the ephemeral key chosen, so the resulting ciphertext's symmetric key is derivable by anyone without possessing any private key — demonstrating that the "encrypt-to-recipient" confidentiality property is broken for this share.

### Citations

**File:** core/services/ocr2/plugins/vault/plugin.go (L837-852)
```go
// broadcastBlobPayloads broadcasts each payload as a blob in parallel to reduce
// Observation() latency (shortening this phase helps the OCR round finish within
// DeltaProgress). Each call is given a 2-second timeout so that a single slow
// broadcast cannot stall the entire batch. No more than 10 broadcasts are allowed
// in flight at a time. Individual broadcast failures are logged and skipped rather
// than aborting the entire observation, so that one problematic payload does not
// prevent the remaining items from being observed. Context cancellation/deadline
// errors on the parent context are propagated immediately so that expired rounds
// fail fast.
func (r *ReportingPlugin) broadcastBlobPayloads(
	ctx context.Context,
	fetcher ocr3_1types.BlobBroadcastFetcher,
	seqNr uint64,
	payloads [][]byte,
	requestIDs [][]string,
) ([][]byte, error) {
```

**File:** core/services/ocr2/plugins/vault/plugin.go (L954-971)
```go
func (s *share) encryptWithKeyBinary(pk string) ([]byte, error) {
	publicKey, err := hex.DecodeString(pk)
	if err != nil {
		return nil, vaulttypes.NewUserError("failed to convert public key to bytes: " + err.Error())
	}

	if len(publicKey) != curve25519.PointSize {
		return nil, vaulttypes.NewUserError(fmt.Sprintf("invalid public key size: expected %d bytes, got %d bytes", curve25519.PointSize, len(publicKey)))
	}

	publicKeyLength := [curve25519.PointSize]byte(publicKey)
	encrypted, err := box.SealAnonymous(nil, s.data, &publicKeyLength, rand.Reader)
	if err != nil {
		return nil, fmt.Errorf("failed to encrypt decryption share: %w", err)
	}

	return encrypted, nil
}
```

**File:** core/services/ocr2/plugins/vault/plugin.go (L1018-1029)
```go
	shares := []*vaultcommon.EncryptedShares{}
	for _, pk := range secretRequest.EncryptionKeys {
		encShare, err := sh.encryptWithKeyBinary(pk)
		if err != nil {
			return nil, err
		}

		shares = append(shares, &vaultcommon.EncryptedShares{
			EncryptionKey: pk,
			BinaryShares:  [][]byte{encShare},
		})
	}
```

**File:** core/services/ocr2/plugins/vault/request_validation.go (L136-151)
```go
func (r *ReportingPlugin) validateGetSecretsRequestItem(
	ctx context.Context,
	secretRequest *vaultcommon.SecretRequest,
	requestsCountForID map[string]int,
) (*vaultcommon.SecretIdentifier, error) {
	id, err := r.validateSecretIdentifier(ctx, secretRequest.Id)
	if err != nil {
		return nil, err
	}

	if err := r.validateDuplicateSecretIdentifierUserError(secretRequest.Id, requestsCountForID); err != nil {
		return nil, err
	}

	return id, nil
}
```
