### Title
Fee-on-Transfer Token Accounting Divergence Enables Irreversible Fund Lock and Unbacked NEAR-Side Credit - (File: evm/src/omni-bridge/contracts/OmniBridge.sol)

### Summary

`OmniBridge.initTransfer` records the caller-supplied `amount` in the `InitTransfer` event without verifying the actual balance increase. For fee-on-transfer ERC20 tokens the bridge receives `amount − fee` but the NEAR side is told `amount`, creating unbacked supply on NEAR and making future `finTransfer` calls on EVM revert due to insufficient balance.

### Finding Description

In the EVM → NEAR direction, `initTransfer` handles native (non-bridge, non-custom-minter) ERC20 tokens with a plain `safeTransferFrom`:

```solidity
// OmniBridge.sol lines 407-411
IERC20(tokenAddress).safeTransferFrom(
    msg.sender,
    address(this),
    amount
);
```

Immediately after, the function emits the event using the caller-supplied `amount` verbatim:

```solidity
// OmniBridge.sol lines 427-436
emit BridgeTypes.InitTransfer(
    msg.sender,
    tokenAddress,
    currentOriginNonce,
    amount,   // ← recorded as-is, not the actual received balance
    fee,
    nativeFee,
    recipient,
    message
);
``` [1](#0-0) [2](#0-1) 

No balance snapshot is taken before or after the transfer to verify that `balanceAfter − balanceBefore == amount`. For a fee-on-transfer token the bridge receives `amount − tokenFee` while the event asserts `amount` was locked.

The NEAR side treats the `InitTransfer` event as the sole source of truth (per the architecture documentation: *"The NEAR side reads this event (via light client or Wormhole) to complete the transfer. Every field needed to reconstruct the transfer must be in the event"*). It therefore credits the full `amount` to the recipient. [3](#0-2) 

When the recipient later bridges back (NEAR → EVM), the NEAR side signs a `TransferMessagePayload` for `amount` tokens and a relayer calls `finTransfer`. The EVM bridge then attempts:

```solidity
// OmniBridge.sol lines 351-354
IERC20(payload.tokenAddress).safeTransfer(
    payload.recipient,
    payload.amount   // ← full amount, but bridge only holds amount − tokenFee
);
``` [4](#0-3) 

This reverts if the bridge's balance of that token is insufficient, permanently locking the user's funds on NEAR with no redemption path.

The same pattern exists in the Starknet `init_transfer`, which also does a plain `transfer_from` without a balance check:

```cairo
// starknet/src/omni_bridge.cairo lines 304-306
let success = IERC20Dispatcher { contract_address: token_address }
    .transfer_from(caller, get_contract_address(), amount.into());
assert(success, 'ERR_TRANSFER_FROM_FAILED');
``` [5](#0-4) 

### Impact Explanation

Two impacts apply simultaneously:

1. **Irreversible fund lock / permanently unclaimable value** (Critical): Every user who bridged a fee-on-transfer token EVM → NEAR and then attempts to redeem on EVM will have their `finTransfer` revert. The NEAR-side transfer message is already finalised and the nonce consumed; there is no refund path. Funds are permanently stranded.

2. **Balance-accounting divergence that breaks backing guarantees** (High): The NEAR side holds a credit of `amount` while the EVM bridge holds only `amount − tokenFee`. The shortfall accumulates with every `initTransfer` call. Other users' legitimate `finTransfer` withdrawals of the same token can be drained to cover the gap, socialising the loss across all depositors of that token.

### Likelihood Explanation

Medium. The bridge imposes no allowlist on which ERC20 tokens may be used in `initTransfer`; any caller can supply any token address. Fee-on-transfer tokens exist on mainnet (e.g. PAXG, STA, tokens with reflection mechanics). A single `initTransfer` with such a token is sufficient to trigger the accounting divergence; no coordination or privileged access is required.

### Recommendation

Record the bridge's token balance before and after the `safeTransferFrom` and use the measured delta as the canonical locked amount in both the internal state and the emitted event:

```solidity
uint256 balanceBefore = IERC20(tokenAddress).balanceOf(address(this));
IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), amount);
uint256 received = IERC20(tokenAddress).balanceOf(address(this)) - balanceBefore;
require(received == amount, "Fee-on-transfer tokens not supported");
// then emit InitTransfer with `received` instead of `amount`
```

Alternatively, explicitly document and enforce (via a registry or `require`) that only non-fee tokens may be bridged as native ERC20 assets. Apply the same fix to the Starknet `init_transfer`.

### Proof of Concept

1. Token `FOT` charges a 1% fee on every transfer.
2. Alice calls `OmniBridge.initTransfer(FOT, 1000, 0, 0, "alice.near", "")`.
3. `safeTransferFrom` moves 1000 FOT from Alice; the bridge receives 990 FOT (10 taken as fee).
4. `InitTransfer` event is emitted with `amount = 1000`.
5. NEAR relayer reads the event and credits Alice's NEAR account with 1000 FOT-wrapped tokens.
6. Alice calls `ft_transfer_call` on NEAR to bridge 1000 tokens back to EVM.
7. NEAR MPC signs a `TransferMessagePayload` for `amount = 1000`.
8. Relayer calls `OmniBridge.finTransfer(sig, payload)`.
9. Bridge attempts `IERC20(FOT).safeTransfer(alice_evm, 1000)` but only holds 990 FOT → **revert**.
10. Alice's 1000 NEAR-side tokens are permanently unclaimable; the 990 FOT held by the bridge is now available to drain other users' withdrawals. [6](#0-5) [2](#0-1) [7](#0-6)

### Citations

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L350-355)
```text
        } else {
            IERC20(payload.tokenAddress).safeTransfer(
                payload.recipient,
                payload.amount
            );
        }
```

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

**File:** evm/CLAUDE.md (L23-23)
```markdown
**EVM → NEAR (initTransfer)**: User calls `initTransfer` which burns/locks tokens on EVM and emits `InitTransfer` with all transfer details (sender, token, amount, fee, nativeFee, recipient, message). In the Wormhole variant, a Wormhole message is also sent. The NEAR side reads this event (via light client or Wormhole) to complete the transfer. Every field needed to reconstruct the transfer must be in the event — it is the only data the NEAR side sees.
```

**File:** starknet/src/omni_bridge.cairo (L304-306)
```text
                let success = IERC20Dispatcher { contract_address: token_address }
                    .transfer_from(caller, get_contract_address(), amount.into());
                assert(success, 'ERR_TRANSFER_FROM_FAILED');
```
