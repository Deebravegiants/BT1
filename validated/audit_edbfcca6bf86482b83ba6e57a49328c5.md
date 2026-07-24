### Title
Fee-on-Transfer Token Accounting Divergence in EVM `initTransfer` — (`evm/src/omni-bridge/contracts/OmniBridge.sol`)

---

### Summary

`OmniBridge.initTransfer` records and emits the caller-supplied `amount` parameter in the `InitTransfer` event without verifying the actual balance received after `safeTransferFrom`. For fee-on-transfer ERC20 tokens, the contract receives fewer tokens than `amount`, but the NEAR settlement layer credits the full `amount` to the destination chain, permanently undercollateralizing the EVM vault.

---

### Finding Description

In `OmniBridge.initTransfer`, when the token is neither a bridge token nor a custom-minter token, the contract executes:

```solidity
IERC20(tokenAddress).safeTransferFrom(
    msg.sender,
    address(this),
    amount
);
``` [1](#0-0) 

Immediately after, the function emits the event using the original caller-supplied `amount`:

```solidity
emit BridgeTypes.InitTransfer(
    msg.sender,
    tokenAddress,
    currentOriginNonce,
    amount,   // ← user-supplied, not actual received balance
    fee,
    nativeFee,
    recipient,
    message
);
``` [2](#0-1) 

There is no pre/post balance check. For a fee-on-transfer ERC20, `safeTransferFrom` succeeds and returns without reverting, but the contract receives `amount - transfer_fee` tokens. The emitted `InitTransfer` event carries the full `amount`, which the NEAR bridge consumes to settle the transfer on the destination chain.

The same pattern exists in the Starknet bridge:

```cairo
let success = IERC20Dispatcher { contract_address: token_address }
    .transfer_from(caller, get_contract_address(), amount.into());
assert(success, 'ERR_TRANSFER_FROM_FAILED');
``` [3](#0-2) 

The Starknet `init_transfer` then emits `amount` verbatim in the `InitTransfer` event without any balance reconciliation. [4](#0-3) 

The NEAR bridge's `ft_on_transfer` entry point is **not** affected by this class of bug because the NEP-141 standard passes the actual transferred amount to the receiver callback, not a caller-supplied value. [5](#0-4) 

---

### Impact Explanation

Every `initTransfer` call with a fee-on-transfer ERC20 token creates a permanent backing deficit:

- EVM vault holds: `amount - transfer_fee`
- NEAR credits to destination: `amount`

The gap (`transfer_fee`) is unbacked supply. Repeated transfers accumulate the deficit. When legitimate users later bridge back from the destination chain to EVM, `finTransfer` attempts to release the full credited amount:

```solidity
IERC20(payload.tokenAddress).safeTransfer(
    payload.recipient,
    payload.amount
);
``` [6](#0-5) 

The vault will eventually be drained below the aggregate outstanding claims, causing `safeTransfer` to revert for later redeemers — a permanent fund lock for those users. This matches the allowed impact: **asset-accounting divergence that breaks backing guarantees** and **irreversible fund lock / permanently unclaimable user value**.

---

### Likelihood Explanation

The `initTransfer` function is fully permissionless — any caller can supply any ERC20 address. [7](#0-6) 

An attacker needs only to:
1. Deploy or identify a fee-on-transfer ERC20 token.
2. Call `initTransfer` with that token and a valid NEAR recipient.

No privileged role, no leaked key, no colluding party is required. The attack is repeatable across multiple transactions, compounding the deficit.

---

### Recommendation

Capture the vault balance before and after `safeTransferFrom` and use the delta as the canonical transfer amount for both event emission and downstream accounting:

```solidity
} else {
    uint256 balanceBefore = IERC20(tokenAddress).balanceOf(address(this));
    IERC20(tokenAddress).safeTransferFrom(
        msg.sender,
        address(this),
        amount
    );
    uint256 balanceAfter = IERC20(tokenAddress).balanceOf(address(this));
    uint256 received = balanceAfter - balanceBefore;
    require(received == amount, "FeeOnTransferNotSupported()");
    // or: amount = uint128(received); if fee-on-transfer tokens are to be supported
}
```

Apply the same fix to `starknet/src/omni_bridge.cairo` `init_transfer` by checking the contract's balance before and after `transfer_from` and asserting equality (or using the delta as the settled amount).

---

### Proof of Concept

1. Deploy a fee-on-transfer ERC20 that deducts 10% on every `transferFrom`.
2. Approve `OmniBridge` for `1000` tokens.
3. Call `OmniBridge.initTransfer(feeToken, 1000, 0, 0, "near:victim.near", "")`.
4. `safeTransferFrom` succeeds; bridge receives `900` tokens.
5. `InitTransfer` event is emitted with `amount = 1000`.
6. NEAR relayer picks up the event and credits `1000` tokens to `victim.near` on the destination chain.
7. Bridge EVM vault is short by `100` tokens per call.
8. After 10 such calls, the vault holds `9000` tokens but has outstanding claims of `10000` — the 10th redeemer's `finTransfer` reverts, permanently locking their funds.

### Citations

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L351-354)
```text
            IERC20(payload.tokenAddress).safeTransfer(
                payload.recipient,
                payload.amount
            );
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L373-380)
```text
    function initTransfer(
        address tokenAddress,
        uint128 amount,
        uint128 fee,
        uint128 nativeFee,
        string calldata recipient,
        string calldata message
    ) external payable whenNotPaused(PAUSED_INIT_TRANSFER) {
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L407-411)
```text
                IERC20(tokenAddress).safeTransferFrom(
                    msg.sender,
                    address(this),
                    amount
                );
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L427-436)
```text
        emit BridgeTypes.InitTransfer(
            msg.sender,
            tokenAddress,
            currentOriginNonce,
            amount,
            fee,
            nativeFee,
            recipient,
            message
        );
```

**File:** starknet/src/omni_bridge.cairo (L304-307)
```text
                let success = IERC20Dispatcher { contract_address: token_address }
                    .transfer_from(caller, get_contract_address(), amount.into());
                assert(success, 'ERR_TRANSFER_FROM_FAILED');
            }
```

**File:** starknet/src/omni_bridge.cairo (L316-330)
```text
            self
                .emit(
                    Event::InitTransfer(
                        InitTransfer {
                            sender: caller,
                            token_address,
                            origin_nonce,
                            amount,
                            fee,
                            native_fee,
                            recipient,
                            message,
                        },
                    ),
                )
```

**File:** near/omni-bridge/src/lib.rs (L257-287)
```rust
    pub fn ft_on_transfer(&mut self, sender_id: AccountId, amount: U128, msg: String) {
        let token_id = env::predecessor_account_id();
        let parsed_msg: BridgeOnTransferMsg = serde_json::from_str(&msg)
            .or_else(|_| serde_json::from_str(&msg).map(BridgeOnTransferMsg::InitTransfer))
            .near_expect(BridgeError::ParseMsg);

        // We can't trust sender_id to pay for storage as it can be spoofed.
        let signer_id = env::signer_account_id();
        let promise_or_promise_index_or_value = match parsed_msg {
            BridgeOnTransferMsg::InitTransfer(init_transfer_msg) => {
                self.init_transfer(sender_id, signer_id, token_id, amount, init_transfer_msg)
            }
            BridgeOnTransferMsg::FastFinTransfer(fast_fin_transfer_msg) => {
                self.fast_fin_transfer(token_id, amount, signer_id, fast_fin_transfer_msg)
            }
            BridgeOnTransferMsg::UtxoFinTransfer(utxo_fin_transfer_msg) => self.utxo_fin_transfer(
                token_id,
                amount,
                &signer_id,
                &sender_id,
                utxo_fin_transfer_msg,
            ),
            BridgeOnTransferMsg::SwapMigratedToken => {
                self.swap_migrated_token(sender_id, token_id, amount)
                    .detach();
                PromiseOrPromiseIndexOrValue::Value(U128(0))
            }
        };

        promise_or_promise_index_or_value.as_return();
    }
```
