### Title
Fee-on-Transfer Token Accounting Divergence in `initTransfer` Creates Unbacked Wrapped Supply — (`evm/src/omni-bridge/contracts/OmniBridge.sol`)

---

### Summary

`OmniBridge.initTransfer` calls `safeTransferFrom` to pull native ERC20 tokens into the bridge vault, then unconditionally emits the caller-supplied `amount` in the `InitTransfer` event and Wormhole message. For fee-on-transfer tokens the vault receives `amount − fee_deducted`, but the cross-chain message records `amount`. The NEAR bridge reads that message and credits the full `amount`, minting more wrapped tokens than were ever locked, breaking the 1:1 backing guarantee.

---

### Finding Description

In `OmniBridge.initTransfer`, the non-bridge-token, non-custom-minter branch locks native ERC20 tokens:

```solidity
// OmniBridge.sol lines 407-411
} else {
    IERC20(tokenAddress).safeTransferFrom(
        msg.sender,
        address(this),
        amount          // ← caller-supplied; actual receipt may be less
    );
}
```

Immediately after, `initTransferExtension` is called with the original `amount` parameter, and the `InitTransfer` event is emitted with the same value:

```solidity
// OmniBridge.sol lines 415-436
initTransferExtension(
    msg.sender, tokenAddress, currentOriginNonce,
    amount,   // ← not the actual received balance
    fee, nativeFee, recipient, message, extensionValue
);

emit BridgeTypes.InitTransfer(
    msg.sender, tokenAddress, currentOriginNonce,
    amount,   // ← same inflated value
    fee, nativeFee, recipient, message
);
```

`OmniBridgeWormhole.initTransferExtension` publishes this `amount` verbatim into the Wormhole VAA:

```solidity
// OmniBridgeWormhole.sol lines 136
Borsh.encodeUint128(amount),
```

On the NEAR side, `fin_transfer_callback` decodes the prover result and uses `init_transfer.amount.0` directly to build the `TransferMessage` that is settled to the recipient:

```solidity
// near/omni-bridge/src/lib.rs line 729
amount: Self::denormalize_amount(init_transfer.amount.0, decimals).into(),
```

No balance snapshot is taken before or after `safeTransferFrom`, so the actual vault increment is never measured. The event/message always carries the caller-supplied `amount`.

---

### Impact Explanation

For any ERC20 token that deducts a fee on transfer (e.g., USDT if its fee switch is enabled, or any deflationary/rebasing token), the bridge vault receives `amount − δ` while the destination chain credits `amount`. Each such transfer inflates the wrapped supply by `δ` without a corresponding locked reserve. An attacker can:

1. Repeatedly bridge fee-on-transfer tokens EVM → NEAR, accumulating `δ` of unbacked wrapped tokens per transfer.
2. Redeem those wrapped tokens back to EVM, draining real reserves that belong to honest depositors.

This is a direct backing-guarantee break: **asset-accounting divergence that sends value to the wrong party and creates unbacked supply** — matching the "High" impact tier.

---

### Likelihood Explanation

USDT's fee is currently 0, but the mechanism exists and can be toggled by Tether. Beyond USDT, numerous fee-on-transfer tokens are in active use (e.g., tokens with auto-liquidity or burn mechanics). The bridge imposes no whitelist or fee-on-transfer guard on the native-token lock path. Any unprivileged user can call `initTransfer` with such a token; no special role or leaked key is required.

---

### Recommendation

Measure the actual vault increment by snapshotting the contract's balance before and after `safeTransferFrom`, and use the delta — not the caller-supplied `amount` — for all downstream accounting, event emission, and cross-chain message construction:

```solidity
uint256 balanceBefore = IERC20(tokenAddress).balanceOf(address(this));
IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), amount);
uint256 actualReceived = IERC20(tokenAddress).balanceOf(address(this)) - balanceBefore;
// use actualReceived in place of amount for the event and extension call
```

Apply the same pattern to the `customMinters` path, where `safeTransferFrom` sends tokens to the minter and `burn(tokenAddress, amount)` is subsequently called — if the minter receives less than `amount`, the burn call may revert or over-burn.

---

### Proof of Concept

1. Deploy or use any ERC20 token that charges a 1% transfer fee.
2. Call `OmniBridge.initTransfer(tokenAddress, 1000e18, 0, 0, nearRecipient, "")`.
3. `safeTransferFrom` moves 1000e18 from the caller; the contract receives 990e18 (1% fee deducted).
4. `InitTransfer` event is emitted with `amount = 1000e18`.
5. Relayer submits proof to NEAR `fin_transfer`; `fin_transfer_callback` reads `init_transfer.amount = 1000e18` and credits 1000e18 wrapped tokens to `nearRecipient`.
6. Vault holds only 990e18; 10e18 of wrapped supply is unbacked.
7. Repeat until the vault is drained relative to outstanding wrapped supply. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L406-412)
```text
            } else {
                IERC20(tokenAddress).safeTransferFrom(
                    msg.sender,
                    address(this),
                    amount
                );
            }
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L415-436)
```text
        initTransferExtension(
            msg.sender,
            tokenAddress,
            currentOriginNonce,
            amount,
            fee,
            nativeFee,
            recipient,
            message,
            extensionValue
        );

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

**File:** evm/src/omni-bridge/contracts/OmniBridgeWormhole.sol (L129-141)
```text
        bytes memory payload = bytes.concat(
            bytes1(uint8(MessageType.InitTransfer)),
            bytes1(omniBridgeChainId),
            Borsh.encodeAddress(sender),
            bytes1(omniBridgeChainId),
            Borsh.encodeAddress(tokenAddress),
            Borsh.encodeUint64(originNonce),
            Borsh.encodeUint128(amount),
            Borsh.encodeUint128(fee),
            Borsh.encodeUint128(nativeFee),
            Borsh.encodeString(recipient),
            Borsh.encodeString(message)
        );
```

**File:** evm/src/omni-bridge/contracts/BridgeTypes.sol (L23-32)
```text
    event InitTransfer(
        address indexed sender,
        address indexed tokenAddress,
        uint64 indexed originNonce,
        uint128 amount,
        uint128 fee,
        uint128 nativeFee,
        string recipient,
        string message
    );
```

**File:** near/omni-bridge/src/lib.rs (L726-736)
```rust
        let transfer_message = TransferMessage {
            origin_nonce: init_transfer.origin_nonce,
            token: init_transfer.token,
            amount: Self::denormalize_amount(init_transfer.amount.0, decimals).into(),
            recipient: init_transfer.recipient,
            fee: Self::denormalize_fee(&init_transfer.fee, decimals),
            sender: init_transfer.sender,
            msg: init_transfer.msg,
            destination_nonce,
            origin_transfer_id: None,
        };
```
