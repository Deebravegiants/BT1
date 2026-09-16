### Title
Relayer reward claims (`OutboundConsensusDeliveryClaim` / `OutboundRequestDeliveryClaim`) only support ECDSA signatures, permanently locking out relayers that deliver messages via smart contract wallets - ([File: modules/utils/crypto/src/verification.rs])

### Summary
Hyperbridge's relayer incentive pallet pays out consensus/request delivery rewards to whichever EVM address is recorded on the destination chain as the message deliverer (`msg.sender` of the relaying transaction, captured in `EvmHost`'s receipt/epoch storage slots). To claim that reward on Hyperbridge, the relayer must produce a `Signature::Evm` that recovers to that exact address. The `Signature::verify` implementation only performs raw secp256k1 ECDSA recovery — there is no ERC‑1271/`SignatureChecker`-style fallback for contract accounts, mirroring the FootiumEscrow bug class where an owner allowed to be a smart-contract wallet cannot produce a signature the contract accepts.

### Finding Description
`Signature::verify` for the `Evm` variant recovers a public key via `sp_io::crypto::secp256k1_ecdsa_recover` and derives the signer as `keccak256(pub_key)[12..]` — a pure ECDSA path with no alternate branch for contract-based signature validation: [1](#0-0) 

This `verify` routine backs the attribution checks in two relayer reward-claim flows:

- `process_outbound_consensus_delivery_claim` recovers the signer from `signature.verify(&msg, None)` and requires it to equal `evm_address`, the address decoded from the `EvmHost._epochs[set_id]` storage slot (i.e., whatever `msg.sender` populated that slot on the destination EVM chain): [2](#0-1) 

- `process_outbound_request_delivery_claim` performs the same check against `delivered_by`, decoded from the `RequestReceipts[commitment]` storage slot on the destination chain: [3](#0-2) 

On the EVM side, this delivery address is populated from `msg.sender`/receipt bookkeeping in `EvmHost.sol` / `HandlerV2.sol` whenever a relayer submits `handleMessages` (or the equivalent consensus update) — i.e., whichever address actually calls the handler is the one that must later sign the claim. If a relayer operates through a smart-contract wallet (a Safe multisig for key-rotation safety, an ERC‑4337 account, or any other AA wallet) to submit these delivery transactions, that contract address becomes the on-chain "delivering relayer." Because a smart-contract address has no private key, it can never produce an ECDSA signature that recovers to itself, and because `Signature::verify` has no ERC‑1271 fallback, that relayer can never satisfy `recovered_address == evm_address` / `recovered == delivered_by`.

### Impact Explanation
Any relayer that delivers hyperbridge-originated consensus updates or requests through a smart-contract wallet permanently forfeits the associated reward: `OutboundConsensusDeliveryReward` / `OutboundRequestDeliveryReward` payouts for that delivery become unclaimable forever, since the on-chain attribution address can never sign a message that passes verification. This is a permanent loss of protocol-funded relayer incentives for the affected message deliveries, satisfying the "permanent freezing of funds" bar — the funds sit in the treasury/allocation and the intended beneficiary (the relayer that did the honest delivery work) has no path to claim them once the delivery has been recorded under a contract address.

### Likelihood Explanation
Using a smart-contract wallet (multisig, ERC‑4337 account, or custodial infra wallet) to sign and submit relaying transactions is a realistic and common operational security practice for relayer operators, especially at scale, and nothing in the protocol prevents or warns against it. No malicious actor is required — an honest relayer following normal operational-security practices for its hot wallet triggers the loss the first time it tries to claim a reward for a delivery made from a contract account.

### Recommendation
Extend `Signature::verify` (and the `Evm` variant specifically) to support ERC‑1271 (`isValidSignature`) validation when the recorded delivery address has contract code, mirroring OpenZeppelin's `SignatureChecker.isValidSignatureNow` pattern recommended in the original Footium report. This requires either an off-chain EVM call from the runtime (not directly possible in a pallet) or, more practically, restructuring the claim so that ECDSA-only attribution is documented as a known constraint and smart-contract relayer wallets instead register/rotate to an EOA signing key that can produce valid claim signatures (an explicit relayer-key-registration mechanism decoupled from the delivery `msg.sender`), so the reward-claim signer need not be the exact contract address that submitted the delivery transaction.

### Proof of Concept
1. A relayer operator deploys/operates a Safe (or any AA smart-contract wallet) as its hot wallet and uses it to submit `handleMessages`/consensus-update transactions on the destination EVM chain, so `EvmHost._epochs[set_id]` (or `RequestReceipts[commitment]`) records the Safe's contract address as the delivering relayer.
2. The operator later builds an `OutboundConsensusDeliveryClaim` / `OutboundRequestDeliveryClaim` and attempts to prove they delivered it by supplying a `Signature::Evm`.
3. Because the Safe has no private key, no valid ECDSA signature exists that recovers to the Safe's address; `signature.verify` in `modules/utils/crypto/src/verification.rs` can only ever recover an EOA-style secp256k1 signer.
4. `ensure!(recovered_address == evm_address, Error::<T>::OutboundSignerMismatch)` in `modules/pallets/relayer/src/outbound_consensus.rs` (and the analogous check in `outbound_request.rs`) always fails, so the reward for that delivery can never be claimed by anyone, permanently orphaning the treasury payout tied to that commitment/set_id.

### Citations

**File:** modules/utils/crypto/src/verification.rs (L41-51)
```rust
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
```

**File:** modules/pallets/relayer/src/outbound_consensus.rs (L164-173)
```rust
		let evm_address = Self::decode_epochs_slot_address(destination, &raw)
			.ok_or(Error::<T>::OutboundDeliveryNotProven)?;

		// Replay protection comes from the `OutboundConsensusRotationsClaimed`
		let msg = outbound_consensus_delivery_message(set_id, destination, payee);
		let recovered = signature.verify(&msg, None).map_err(|_| Error::<T>::InvalidSignature)?;
		let recovered_address = Address::try_from(recovered.as_slice())
			.map_err(|_| Error::<T>::OutboundSignerMismatch)?;
		ensure!(recovered_address == evm_address, Error::<T>::OutboundSignerMismatch);

```

**File:** modules/pallets/relayer/src/outbound_request.rs (L169-173)
```rust
		let delivered_by = Self::decode_receipt_relayer(destination, &raw)?;

		let msg = outbound_request_delivery_message(commitment, destination, payee);
		let recovered = signature.verify(&msg, None).map_err(|_| Error::<T>::InvalidSignature)?;
		ensure!(recovered == delivered_by, Error::<T>::OutboundRequestSignerMismatch);
```
