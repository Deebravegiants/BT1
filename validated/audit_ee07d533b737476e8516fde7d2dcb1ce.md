Found it: `extract_signer` in `modules/pallets/ismp/src/host.rs:351-359` implements exactly the same class of bug as CVE-2025-11561 — an unauthenticated identity-mapping fallback keyed only on length, with no cryptographic verification tying the claimed identity to the actual message.

### Title
Unverified relayer-identity fallback in `extract_signer` lets any deliverer forge `RequestReceipts` attribution and steal relayer rewards - ([File: modules/pallets/ismp/src/host.rs])

### Summary
`extract_signer` (`modules/pallets/ismp/src/host.rs:351-359`), used by `store_request_receipt`/`store_response_receipt` when `handle_unsigned` delivers a `Request`/`Response` batch, decides how to interpret the caller-supplied `msg.signer` bytes purely by length: ≤32 bytes are taken verbatim as the "signer" identity, >32 bytes are decoded as a `Signature` and `.signer()` is extracted — in neither branch is a cryptographic signature actually verified over the delivered request/response before the identity is written into `RequestReceipts`/`ResponseReceipts`. This mirrors the SSSD flaw: two different identity-resolution paths exist (direct bytes vs. decoded-signature `an2ln`-style extraction), selected by an untrusted, attacker-controlled signal (byte length), with no proof of possession backing either path.

### Finding Description
`handle_unsigned` is a `ValidateUnsigned` extrinsic [1](#0-0) , so any unprivileged relayer can submit a `RequestMessage`/`ResponseMessage` whose `signer: Vec<u8>` field is fully attacker-chosen. On dispatch, `modules/ismp/core/src/handlers/request.rs:112` calls `host.store_request_receipt(&wrapped_req, &msg.signer)?`, which delegates to `extract_signer`: [2](#0-1) 

Neither branch checks that `msg.signer` is a valid signature *over the actual delivered request*. The `> 32` branch merely SCALE-decodes any bytes that parse as a `Signature` enum and reads back the embedded public key/address (`Signature::signer()`), without calling `Signature::verify`. The `<= 32` branch stores the raw bytes as-is. Consequently, an attacker delivering a batch through `handle_unsigned` can set `msg.signer` to an arbitrary encoded `Signature::Evm{ address: <victim>, signature: <anything 65 bytes> }` (or any account's raw 32-byte public key) and have that identity permanently recorded in `RequestReceipts[commitment]`/`ResponseReceipts[commitment]` as "the relayer who delivered this message" — regardless of who actually delivered it.

This directly poisons `pallet-relayer`'s reward-attribution logic, which trusts this receipt as the source of truth:
- `decode_receipt_relayer` in `modules/pallets/relayer/src/accumulate.rs:322-351` decodes the stored receipt using the exact same length-based, unverified logic.
- `process_outbound_request_delivery_claim` in `modules/pallets/relayer/src/outbound_request.rs:169-173` reads `delivered_by` from that receipt and pays `payee` whenever a submitted signature recovers to `delivered_by` — but since `delivered_by` was never cryptographically tied to a real deliverer, an attacker can plant themselves (or forge a delivery attribution for a completely unrelated address) as the recorded relayer with zero possession of any relevant private key on the destination chain, since no delivery-time signature is actually checked.
- The `accumulate_fees` fee-crediting path (`modules/pallets/relayer/src/accumulate.rs`) is fed by the same unverified receipt and credits `Fees[state_machine][address]` to whatever identity was planted.

Effectively, the "signer" field on `handle_unsigned` messages functions like SSSD's `userPrincipalName`/`samAccountName` — an attacker-writable identity claim that a fallback resolution path (length-based dispatch here, plugin fallback there) accepts without verifying possession, letting the caller impersonate an arbitrary account for downstream privileged accounting (fee/reward payout) rather than for authentication itself.

### Impact Explanation
This is a fund-theft path against pallet-relayer's incentive accounting: an attacker can direct message-delivery rewards and accumulated fees to accounts they don't control the delivery of, or falsely attribute deliveries, corrupting `Fees[state_machine][address]` balances and `OutboundRequestDeliveryReward` payouts and enabling unauthorized draining of the treasury via `claim_outbound_request_delivery_reward` / `withdraw_fees`, since payout eligibility is keyed entirely off the unverified receipt identity. This satisfies "theft of funds" / "unauthorized app action" impact categories — High severity given it is reachable by any unprivileged relayer submitting an unsigned extrinsic.

### Likelihood Explanation
High likelihood: `handle_unsigned` requires no privilege (`ensure_none`), and crafting a >32-byte `Vec<u8>` that SCALE-decodes as a `Signature::Evm`/`Sr25519`/`Ed25519` with an attacker-chosen embedded address/public key is trivial and needs no valid cryptographic signature — `extract_signer`'s `>32` branch never calls `.verify()`, only `.signer()`.

### Recommendation
`extract_signer` must cryptographically verify the decoded `Signature` against the actual request/response payload (as `outbound_request_delivery_message`/`accumulate` claims already do) before trusting `.signer()`, or the receipt attribution must be tied to an already-verified proof of delivery (e.g., the extrinsic's origin/signed identity) rather than an arbitrary caller-supplied byte blob. At minimum, treat the two branches uniformly and require signature verification in both, eliminating any length-based unauthenticated fallback for identity resolution feeding financial accounting.

### Proof of Concept
1. Attacker (unprivileged) builds a `PostRequest`/`GetRequest` batch destined for this chain and a valid state/membership proof (or Get-response proof) as normal.
2. Sets `RequestMessage.signer` (or `ResponseMessage.signer`) to `Signature::Evm { address: victim_or_self_address, signature: [0u8;65] }.encode()` — a >32-byte blob that SCALE-decodes cleanly but carries an unverifiable/garbage signature.
3. Submits via `Ismp::handle_unsigned` / `StateCoprocessor::handle_unsigned`. `validate_unsigned` re-runs `handle_get_requests`/dispatch logic but never calls `Signature::verify` on `msg.signer` — see `extract_signer` at `modules/pallets/ismp/src/host.rs:351-359` — so the extrinsic succeeds and `RequestReceipts[commitment]` is set to `victim_or_self_address`.
4. Attacker (or an EVM signer they control matching that address for the delivery-claim step) later calls `claim_outbound_request_delivery_reward`/`accumulate_fees` referencing this commitment; `decode_receipt_relayer` reads back the planted address and pays the reward to `payee`, even though the attacker never performed a genuine, verifiable delivery signed by that key at message-handling time.

### Citations

**File:** modules/pallets/state-coprocessor/src/lib.rs (L92-104)
```rust
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			message: GetRequestsWithProof,
		) -> DispatchResult {
			ensure_none(origin)?;

			Self::handle_get_requests(message).map_err(|err| {
				log::error!(target: "ismp", "pallet-coprocessor: {:?}", err);
				Error::<T>::HandlingError
			})?;

			Ok(())
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
