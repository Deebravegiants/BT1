### Title
Fee-on-Transfer Token Accounting Divergence Creates Unbacked Wrapped Supply — (`evm/src/omni-bridge/contracts/OmniBridge.sol`)

### Summary

`OmniBridge.initTransfer` and the Starknet equivalent `omni_bridge.init_transfer` emit the caller-supplied `amount` in the `InitTransfer` event without verifying the actual balance received after `safeTransferFrom`. For fee-on-transfer ERC20 tokens the bridge custodies less than it claims, causing NEAR to mint more wrapped tokens than are backed, permanently breaking the 1:1 collateral guarantee.

### Finding Description

In `OmniBridge.initTransfer`, the locked-token path performs:

```solidity
// OmniBridge.sol lines 407-411
IERC20(tokenAddress).safeTransferFrom(
    msg.sender,
    address(this),
    amount          // caller-controlled
);
```

Immediately after, without any before/after balance snapshot, the function emits:

```solidity
// OmniBridge.sol lines 427-436
emit BridgeTypes.InitTransfer(
    msg.sender,
    tokenAddress,
    currentOriginNonce,
    amount,          // same caller-controlled value, not actual received
    fee,
    nativeFee,
    recipient,
    message
);
```

The NEAR contract (`near/omni-bridge/src/lib.rs`) consumes this event and credits the user with the full `amount`. If the token deducts a transfer fee, the bridge holds `amount − δ` but NEAR mints `amount` wrapped tokens — a deficit of `δ` per deposit.

The identical pattern exists in Starknet:

```cairo
// omni_bridge.cairo lines 304-306
let success = IERC20Dispatcher { contract_address: token_address }
    .transfer_from(caller, get_contract_address(), amount.into());
// ...emits InitTransfer with `amount` unchanged
```

### Impact Explanation

Every deposit of a fee-on-transfer token widens the gap between locked collateral and outstanding wrapped supply. When users redeem wrapped tokens on NEAR, `finTransfer` on EVM attempts to release the full `amount` from bridge custody. Because the bridge is undercollateralized, later redeemers cannot withdraw — their funds are permanently unclaimable. This satisfies the **High** impact criterion: "balance-accounting divergence that breaks backing guarantees" and "irreversible fund lock / permanently unclaimable user value."

### Likelihood Explanation

Several production ERC20 tokens have fee-on-transfer mechanics (e.g., PAXG, STA, early USDT variants). Any such token that is registered with the bridge (via `deployToken` / `logMetadata`) and used by an unprivileged caller through the public `initTransfer` entrypoint triggers the bug. No privileged access is required beyond the token being listed.

### Recommendation

Capture the bridge's token balance before and after `safeTransferFrom` and use the delta as the canonical `amount` for both the event and any downstream accounting:

```solidity
uint256 balanceBefore = IERC20(tokenAddress).balanceOf(address(this));
IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), amount);
uint256 actualReceived = IERC20(tokenAddress).balanceOf(address(this)) - balanceBefore;
// use actualReceived in place of amount for the event and extension call
```

Apply the same fix to the Starknet `init_transfer`.

### Proof of Concept

1. A fee-on-transfer token `FOT` (2% fee) is registered with the bridge.
2. Attacker calls `OmniBridge.initTransfer(FOT, 1000, 0, 0, "attacker.near", "")`.
3. Bridge receives 980 FOT (`safeTransferFrom` deducts 20 as fee).
4. `InitTransfer` event emits `amount = 1000`.
5. NEAR prover processes the event; NEAR bridge mints 1000 wrapped-FOT to `attacker.near`.
6. Attacker bridges 1000 wrapped-FOT back; NEAR burns 1000 and signals EVM to release 1000 FOT.
7. `finTransfer` sends 1000 FOT from bridge custody — but bridge only holds 980 from this deposit.
8. After enough such deposits the bridge is drained; honest depositors cannot redeem. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

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

**File:** starknet/src/omni_bridge.cairo (L303-307)
```text
            } else {
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
