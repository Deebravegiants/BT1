### Title
Fee-on-Transfer Token Accounting Divergence Creates Unbacked Cross-Chain Supply — (`evm/src/omni-bridge/contracts/OmniBridge.sol`)

### Summary

`OmniBridge.initTransfer` calls `safeTransferFrom` with the caller-supplied `amount` and immediately emits `InitTransfer` with that same `amount`. For fee-on-transfer (deflationary) ERC20 tokens, the bridge receives fewer tokens than `amount`, but the event — which is the sole data source the NEAR side uses to credit the user — records the full `amount`. This creates unbacked wrapped supply on NEAR and progressively drains the EVM bridge's locked-token reserve.

### Finding Description

In `OmniBridge.initTransfer`, the non-bridge-token lock path is:

```solidity
// OmniBridge.sol lines 407–411
IERC20(tokenAddress).safeTransferFrom(
    msg.sender,
    address(this),
    amount
);
```

followed immediately by:

```solidity
// OmniBridge.sol lines 427–436
emit BridgeTypes.InitTransfer(
    msg.sender,
    tokenAddress,
    currentOriginNonce,
    amount,   // ← caller-supplied, not actual-received
    fee,
    nativeFee,
    recipient,
    message
);
```

`SafeERC20.safeTransferFrom` only checks that the call did not revert and that the return value (if any) is `true`. It does **not** compare the contract's pre- and post-transfer balance to verify the actual received amount. For a fee-on-transfer token with a transfer fee of `f`, the bridge receives `amount - f` but the event records `amount`.

The NEAR bridge reads this event via a light-client or Wormhole proof in `fin_transfer_callback`:

```rust
// near/omni-bridge/src/lib.rs line 729
amount: Self::denormalize_amount(init_transfer.amount.0, decimals).into(),
```

`init_transfer.amount` is decoded directly from the EVM event log — it is the caller-supplied `amount`, not the actual received amount. NEAR then mints or unlocks the full `amount` on the destination chain.

The same pattern exists in the Starknet bridge:

```cairo
// starknet/src/omni_bridge.cairo lines 304–306
let success = IERC20Dispatcher { contract_address: token_address }
    .transfer_from(caller, get_contract_address(), amount.into());
assert(success, 'ERR_TRANSFER_FROM_FAILED');
```

followed by emitting `InitTransfer` with the original `amount`.

### Impact Explanation

Every `initTransfer` call with a fee-on-transfer token creates a deficit: the EVM bridge holds `amount - f` tokens but NEAR credits `amount`. Over repeated transfers the EVM bridge's locked reserve becomes progressively undercollateralized. When users bridge back from NEAR to EVM, `finTransfer` attempts to release the full credited amount:

```solidity
// OmniBridge.sol lines 351–354
IERC20(payload.tokenAddress).safeTransfer(
    payload.recipient,
    payload.amount
);
```

Eventually the bridge cannot fulfill redemptions — either reverting (freezing user funds) or, if the token's own `transfer` silently short-pays, sending less than the signed amount. This breaks the bridge's backing guarantee and matches the allowed impact: **balance-accounting divergence that breaks backing guarantees** and **irreversible fund lock / frozen redemption path**.

### Likelihood Explanation

The non-bridge-token path in `initTransfer` has no token whitelist — any ERC20 address is accepted. The NEAR side requires the token to be registered (decimals must exist in `token_decimals`), but registration is a normal operational step for any token the bridge supports. USDT has a built-in fee switch that has historically been set to 0 but can be enabled by the Tether issuer at any time. Other fee-on-transfer tokens (e.g., STA, PAXG in some configurations) are in active use. A single governance action by a token issuer — entirely outside the bridge's control — is sufficient to trigger the vulnerability for any already-registered token.

### Recommendation

Measure the actual received amount by comparing balances before and after the transfer, and use the measured amount in the event:

```solidity
uint256 balanceBefore = IERC20(tokenAddress).balanceOf(address(this));
IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), amount);
uint256 actualReceived = IERC20(tokenAddress).balanceOf(address(this)) - balanceBefore;
require(actualReceived == amount, "FEE_ON_TRANSFER_NOT_SUPPORTED");
// or: use actualReceived (cast to uint128) in the event instead of amount
```

The stricter option (revert if actual ≠ expected) is simpler and prevents silent undercollateralization. Apply the same fix to the Starknet `init_transfer`. Additionally, document fee-on-transfer and rebasing tokens as unsupported in the token-registration process so operators do not register them.

### Proof of Concept

1. A fee-on-transfer ERC20 token `FOT` with a 1% transfer fee is registered with the Omni Bridge on both EVM and NEAR (normal operational step).
2. Attacker (or any user) calls `OmniBridge.initTransfer(FOT, 1_000_000, 0, 0, "near:alice.near", "")`.
3. `safeTransferFrom` moves `990_000` FOT tokens into the bridge (1% fee taken by the token contract). The bridge now holds `990_000` FOT.
4. `InitTransfer` is emitted with `amount = 1_000_000`.
5. A relayer submits the proof to NEAR. `fin_transfer_callback` decodes `amount = 1_000_000` and mints/unlocks `1_000_000` FOT-wrapped tokens on NEAR for `alice.near`.
6. Alice bridges back: NEAR burns `1_000_000` wrapped tokens, MPC signs a `finTransfer` payload for `1_000_000` FOT on EVM.
7. `finTransfer` calls `safeTransfer(alice, 1_000_000)`. The bridge only holds `990_000` FOT → the call reverts, permanently locking Alice's funds.
8. Repeating step 2–5 ten times creates a `100_000` FOT deficit; the bridge becomes insolvent for the last redeemer. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L351-354)
```text
            IERC20(payload.tokenAddress).safeTransfer(
                payload.recipient,
                payload.amount
            );
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

**File:** near/omni-bridge/src/lib.rs (L726-729)
```rust
        let transfer_message = TransferMessage {
            origin_nonce: init_transfer.origin_nonce,
            token: init_transfer.token,
            amount: Self::denormalize_amount(init_transfer.amount.0, decimals).into(),
```

**File:** starknet/src/omni_bridge.cairo (L304-306)
```text
                let success = IERC20Dispatcher { contract_address: token_address }
                    .transfer_from(caller, get_contract_address(), amount.into());
                assert(success, 'ERR_TRANSFER_FROM_FAILED');
```
