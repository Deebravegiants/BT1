This is a real analog: `extract_signer` in `modules/pallets/ismp/src/host.rs` decodes the caller-supplied `Signature` blob and calls `.signer()` to derive the relayer identity used for fee attribution — without ever calling `Signature::verify(...)`, the method on the same type that actually performs the cryptographic check (`sp_io::crypto::secp256k1_ecdsa_recover`, `sr25519_verify`, `ed25519_verify`).

### Title
Relayer/receipt attribution accepts an unverified signature-decode as proof of signer identity - (File: modules/pallets/ismp/src/host.rs)

### Summary
`store_request_receipt` and `store_response_receipt` derive the "signer" recorded against a request/response receipt by calling `extract_signer`, which only SCALE-decodes the submitted bytes into the `Signature` enum and reads back the embedded public key/address via `Signature::signer()`. It never calls `Signature::verify()`, the sibling method in `modules/utils/crypto/src/verification.rs` that performs the actual cryptographic check (`secp256k1_ecdsa_recover`, `sr25519_verify`, `ed25519_verify`) against a message hash. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
This mirrors the CVE-2026-89086 bug class: a signature-bearing structure decodes successfully and the code treats that as proof of validity, skipping the step that ties the signature back to the claimed public key over the actual message. Here, `extract_signer` takes the raw `signer: &Vec<u8>` bytes passed into `store_request_receipt`/`store_response_receipt`, and if longer than 32 bytes, decodes them as a `Signature` (`Evm`/`Sr25519`/`Ed25519` variant), then immediately returns `sig.signer()` — the embedded public key/address field taken directly from attacker-controlled input, with no signature verification against any message (e.g., the request/response hash) ever performed. [4](#0-3) [1](#0-0) 

Since `Signature::signer()` simply echoes back whatever address/public-key bytes were embedded in the decoded structure regardless of whether `signature` bytes inside it are valid, any caller can construct an SCALE-encoded `Signature::Evm { address: <arbitrary>, signature: <arbitrary 65 bytes> }` (or the Sr25519/Ed25519 equivalents) and have `extract_signer` return that arbitrary address as the recorded relayer/signer, with zero cryptographic proof of control over it.

### Impact Explanation
`ResponseReceipt.relayer` (from `store_response_receipt`) and the signer recorded via `store_request_receipt` are used by pallet-ismp's relayer fee/reward accounting to determine who is credited for delivering a request/response. If this signer field feeds fee payout or reward distribution logic downstream, an attacker can forge an arbitrary "signer" identity for a receipt without possessing the corresponding private key, allowing theft/misdirection of relayer fees to an address the caller does not control (or to their own address while impersonating another relayer's key format). This directly implicates "relayer fee and reward accounting," one of the explicitly in-scope Hyperbridge paths.

### Likelihood Explanation
`store_request_receipt`/`store_response_receipt` are exercised on the standard message-delivery path for `pallet-ismp`, reachable by any unprivileged relayer submitting a `handle`/response call with an attacker-chosen `signer` byte-string. No special privilege is required — only that the caller can invoke the normal message-handling entry point and supply the signer bytes that flow into `extract_signer`. [5](#0-4) 

### Recommendation
In `extract_signer`, require that a decoded `Signature` be verified via `Signature::verify(&msg_hash, None)` (binding it to the request/response hash or another caller-committed message) before returning `sig.signer()`. Never return a public key/address extracted from an unverified signature payload as an authenticated identity.

### Proof of Concept
1. Craft bytes `signer_bytes` that SCALE-encode `crypto_utils::verification::Signature::Evm { address: <victim_or_arbitrary_address>, signature: <any 65-byte value> }`, ensuring `signer_bytes.len() > 32`.
2. Call the pallet-ismp entry point that ultimately invokes `store_request_receipt`/`store_response_receipt` with this `signer_bytes` value.
3. `extract_signer` decodes the bytes successfully (`Signature::decode` succeeds), then calls `.signer()`, returning `address` verbatim — no cryptographic check is performed since `Signature::verify` is never invoked.
4. The forged address is persisted in `child_trie::RequestReceipts`/`ResponseReceipts` as the attributed signer/relayer, which downstream fee/reward accounting can consume as if it were cryptographically authenticated. [4](#0-3) [1](#0-0)

### Citations

**File:** modules/pallets/ismp/src/host.rs (L261-283)
```rust
	fn store_request_receipt(&self, req: &Request, signer: &Vec<u8>) -> Result<Vec<u8>, Error> {
		let signer = extract_signer(signer)?;

		let hash = hash_request::<Self>(req);
		child_trie::RequestReceipts::<T>::insert(hash, &signer);
		Ok(signer)
	}

	fn store_response_receipt(
		&self,
		res: &GetResponse,
		signer: &Vec<u8>,
	) -> Result<Vec<u8>, Error> {
		let signer = extract_signer(signer)?;

		let hash = hash_request::<Self>(&res.request());
		let response = hash_response::<Self>(&res);
		child_trie::ResponseReceipts::<T>::insert(
			hash,
			ResponseReceipt { response, relayer: signer.clone() },
		);
		Ok(signer)
	}
```

**File:** modules/pallets/ismp/src/host.rs (L351-359)
```rust
fn extract_signer(signer: &[u8]) -> Result<Vec<u8>, Error> {
	if signer.len() > 32 {
		Signature::decode(&mut signer.as_ref())
			.map(|sig| sig.signer())
			.map_err(|_| Error::SignatureDecodingFailed)
	} else {
		Ok(signer.to_vec())
	}
}
```

**File:** modules/utils/crypto/src/verification.rs (L32-72)
```rust
impl Signature {
	/// verify the signature with the public key in the enum or optionally provide a public key
	/// to be used to verify the signature
	pub fn verify(
		&self,
		msg: &[u8; 32],
		public_key_op: Option<Vec<u8>>,
	) -> Result<Vec<u8>, anyhow::Error> {
		match self {
			Signature::Evm { signature, .. } => {
				if signature.len() != 65 {
					Err(anyhow!("Invalid Signature"))?
				}

				let mut sig = [0u8; 65];
				sig.copy_from_slice(&signature);
				let pub_key = sp_io::crypto::secp256k1_ecdsa_recover(&sig, msg)
					.map_err(|_| anyhow!("Signature Verification failed"))?;
				let signer = sp_io::hashing::keccak_256(&pub_key[..])[12..].to_vec();
				Ok(signer)
			},
			Signature::Sr25519 { signature, public_key } => {
				Self::verify_sr25519(signature, public_key, msg, &public_key_op)?;
				Ok(public_key_op.unwrap_or(public_key.clone()))
			},
			Signature::Ed25519 { signature, public_key, .. } => {
				let signature =
					signature.as_slice().try_into().map_err(|_| anyhow!("Invalid Signature"))?;
				let pub_key = public_key_op
					.clone()
					.unwrap_or(public_key.clone())
					.as_slice()
					.try_into()
					.map_err(|_| anyhow!("Invalid Public Key"))?;
				if !sp_io::crypto::ed25519_verify(&signature, msg, &pub_key) {
					Err(anyhow!("Signature Verification failed"))?
				}
				Ok(public_key_op.unwrap_or(public_key.clone()))
			},
		}
	}
```

**File:** modules/utils/crypto/src/verification.rs (L109-115)
```rust
	pub fn signer(&self) -> Vec<u8> {
		match self {
			Signature::Evm { address, .. } => address.clone(),
			Signature::Sr25519 { public_key, .. } => public_key.clone(),
			Signature::Ed25519 { public_key, .. } => public_key.clone(),
		}
	}
```
