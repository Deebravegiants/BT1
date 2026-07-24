### Title
STRK Native Fees Permanently Locked in Starknet Bridge — (File: `starknet/src/omni_bridge.cairo`)

---

### Summary

The Starknet `OmniBridge` collects STRK native fees from users during `init_transfer` by pulling them into `get_contract_address()`. No function in the contract ever releases those STRK tokens to any fee recipient. Every STRK native fee paid by every user accumulates in the contract permanently.

---

### Finding Description

In `init_transfer`, when `native_fee > 0`, the bridge pulls STRK from the caller into itself: [1](#0-0) 

```cairo
if native_fee > 0 {
    let native_token = self.strk_token_address.read();
    let success = IERC20Dispatcher { contract_address: native_token }
        .transfer_from(caller, get_contract_address(), native_fee.into());
    assert(success, 'ERR_FEE_TRANSFER_FAILED');
}
```

The destination is `get_contract_address()` — the bridge itself. [1](#0-0) 

The entire public interface of the contract is: [2](#0-1) 

`log_metadata`, `deploy_token`, `fin_transfer`, `init_transfer`, `upgrade_token`, `set_pause_flags`, `pause_all`, `get_token_address`, `is_bridge_token`, `is_transfer_finalised`. **None of these release STRK.**

`fin_transfer` (inbound, NEAR→Starknet) receives a `fee_recipient` field in the payload but only emits it in an event — it transfers nothing to it: [3](#0-2) 

On the NEAR side, when a Starknet→NEAR transfer is finalized, the NEAR bridge **mints** wrapped STRK to the relayer: [4](#0-3) 

```rust
if transfer_message.fee.native_fee.0 > 0 {
    let native_token_id = self.get_native_token_id(transfer_message.get_origin_chain());
    ext_token::ext(native_token_id)
        .with_static_gas(MINT_TOKEN_GAS)
        .mint(fee_recipient.clone(), transfer_message.fee.native_fee, None)
        .detach();
}
```

The relayer is compensated in freshly-minted wrapped STRK on NEAR, while the real STRK on Starknet is never released. The two sides are permanently decoupled: real STRK accumulates in the Starknet bridge with no exit path.

---

### Impact Explanation

Every `init_transfer` call with `native_fee > 0` irreversibly locks real STRK in the Starknet bridge contract. There is no admin rescue function, no fee-claim function, and no upgrade-triggered withdrawal in the current code. This is a **Critical** irreversible fund lock of user-paid fee value in the bridge fee flow.

---

### Likelihood Explanation

Any unprivileged user calling `init_transfer` with a non-zero `native_fee` triggers the lock. This is a normal, documented protocol operation. Likelihood is **High** — every relayer-incentivized transfer from Starknet contributes to the locked balance.

---

### Recommendation

Add a permissioned STRK withdrawal function to the Starknet bridge (e.g., callable by `DEFAULT_ADMIN_ROLE` or a designated fee-collector address) that transfers accumulated STRK native fees out of the contract. Alternatively, release the STRK directly to the `fee_recipient` inside `fin_transfer` when processing the corresponding inbound leg, mirroring the NEAR-side `send_fee_internal` pattern.

---

### Proof of Concept

1. User calls `init_transfer` on Starknet with `native_fee = 1_000e18` STRK.
2. `transfer_from(caller, get_contract_address(), 1_000e18)` executes — STRK is now in the bridge.
3. Relayer observes the `InitTransfer` event and calls `fin_transfer` on NEAR.
4. NEAR bridge mints 1_000e18 wrapped STRK to the relayer via `mint(fee_recipient, ...)`.
5. The 1_000e18 real STRK on Starknet remains in the bridge contract.
6. No function exists to retrieve it. Repeat for every transfer with a native fee.

### Citations

**File:** starknet/src/omni_bridge.cairo (L9-32)
```text
pub trait IOmniBridge<TContractState> {
    fn log_metadata(ref self: TContractState, token: ContractAddress);
    fn deploy_token(ref self: TContractState, signature: Signature, payload: MetadataPayload);
    fn fin_transfer(
        ref self: TContractState, signature: Signature, payload: TransferMessagePayload,
    );
    fn init_transfer(
        ref self: TContractState,
        token_address: ContractAddress,
        amount: u128,
        fee: u128,
        native_fee: u128,
        recipient: ByteArray,
        message: ByteArray,
    );
    fn upgrade_token(
        ref self: TContractState, token_address: ContractAddress, new_class_hash: ClassHash,
    );
    fn set_pause_flags(ref self: TContractState, flags: u8);
    fn pause_all(ref self: TContractState);
    fn get_token_address(self: @TContractState, token_id: ByteArray) -> ContractAddress;
    fn is_bridge_token(self: @TContractState, token_address: ContractAddress) -> bool;
    fn is_transfer_finalised(self: @TContractState, nonce: u64) -> bool;
}
```

**File:** starknet/src/omni_bridge.cairo (L242-279)
```text
        fn fin_transfer(
            ref self: ContractState, signature: Signature, payload: TransferMessagePayload,
        ) {
            assert(!_is_paused(@self, PAUSE_FIN_TRANSFER), 'ERR_FIN_TRANSFER_PAUSED');

            assert(
                !self.is_transfer_finalised(payload.destination_nonce), 'ERR_NONCE_ALREADY_USED',
            );
            _set_transfer_finalised(ref self, payload.destination_nonce);

            _verify_borsh_signature(
                ref self, @payload.to_borsh(self.omni_bridge_chain_id.read()), signature,
            );

            if self.is_bridge_token(payload.token_address) {
                IBridgeTokenDispatcher { contract_address: payload.token_address }
                    .mint(payload.recipient, payload.amount.into());
            } else {
                let success = IERC20Dispatcher { contract_address: payload.token_address }
                    .transfer(payload.recipient, payload.amount.into());
                assert(success, 'ERR_TRANSFER_FAILED');
            }

            self
                .emit(
                    Event::FinTransfer(
                        FinTransfer {
                            origin_chain: payload.origin_chain,
                            origin_nonce: payload.origin_nonce,
                            token_address: payload.token_address,
                            amount: payload.amount,
                            recipient: payload.recipient,
                            fee_recipient: payload.fee_recipient,
                            message: payload.message,
                        },
                    ),
                )
        }
```

**File:** starknet/src/omni_bridge.cairo (L309-314)
```text
            if native_fee > 0 {
                let native_token = self.strk_token_address.read();
                let success = IERC20Dispatcher { contract_address: native_token }
                    .transfer_from(caller, get_contract_address(), native_fee.into());
                assert(success, 'ERR_FEE_TRANSFER_FAILED');
            }
```

**File:** near/omni-bridge/src/lib.rs (L1741-1748)
```rust
            if transfer_message.fee.native_fee.0 > 0 {
                let native_token_id = self.get_native_token_id(transfer_message.get_origin_chain());

                ext_token::ext(native_token_id)
                    .with_static_gas(MINT_TOKEN_GAS)
                    .mint(fee_recipient.clone(), transfer_message.fee.native_fee, None)
                    .detach();
            }
```
