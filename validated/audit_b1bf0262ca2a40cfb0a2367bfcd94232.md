The vulnerability is real and concrete. Let me confirm the exact lines before writing up the finding.

### Title
Fee-on-Transfer ERC20 Overcredits NEAR While Undercollateralizing EVM Bridge — (`evm/src/omni-bridge/contracts/OmniBridge.sol`)

---

### Summary

`initTransfer` uses the caller-supplied `amount` parameter in the `InitTransfer` event without measuring the actual tokens received. For fee-on-transfer ERC20s, the bridge holds less than it signals to NEAR, breaking the 1:1 backing invariant on every such transfer.

---

### Finding Description

In the `else` branch of `initTransfer` (for non-bridge, non-custom-minter ERC20s), the contract executes:

```solidity
// OmniBridge.sol lines 407–411
IERC20(tokenAddress).safeTransferFrom(
    msg.sender,
    address(this),
    amount          // ← requested amount, not actual received amount
);
``` [1](#0-0) 

Immediately after, the event is emitted using the same caller-supplied `amount`:

```solidity
// OmniBridge.sol lines 427–436
emit BridgeTypes.InitTransfer(
    msg.sender,
    tokenAddress,
    currentOriginNonce,
    amount,          // ← original param, not balance delta
    ...
);
``` [2](#0-1) 

There is **no balance-before/balance-after check** between the `safeTransferFrom` call and the event emission. For a fee-on-transfer token with tax rate `t`, `safeTransferFrom(msg.sender, address(this), amount)` delivers only `amount*(1-t)` to the bridge, but `InitTransfer.amount` carries the full `amount`.

The `InitTransfer` event is the sole cross-chain signal. NEAR reads it and credits the recipient with the full `amount`. [3](#0-2) 

On the return path, `finTransfer` releases the full `payload.amount` from bridge reserves:

```solidity
// OmniBridge.sol line 351
IERC20(payload.tokenAddress).safeTransfer(payload.recipient, payload.amount);
``` [4](#0-3) 

---

### Impact Explanation

Every `initTransfer` call with a fee-on-transfer token creates a shortfall of `amount * t` tokens in the bridge's EVM reserves. The bridge is undercollateralized by exactly the transfer tax on each such call. If enough transfers accumulate, `finTransfer` calls for that token will fail (insufficient balance), permanently locking or losing funds for honest users who bridged back from NEAR. This is a direct violation of the backing guarantee: EVM-locked collateral must equal NEAR-credited supply.

---

### Likelihood Explanation

Fee-on-transfer tokens are a well-known ERC20 variant (USDT has had the feature in its contract, various DeFi tokens use it). The `initTransfer` function has no token whitelist — any ERC20 address is accepted in the `else` branch. An unprivileged user needs only to call `initTransfer` with such a token; no special role, key, or colluding party is required. [5](#0-4) 

---

### Recommendation

Replace the fixed-`amount` transfer with a balance-delta pattern to derive the actual received amount, and use that value in both `initTransferExtension` and the `InitTransfer` event:

```solidity
uint256 balanceBefore = IERC20(tokenAddress).balanceOf(address(this));
IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), amount);
uint256 actualReceived = IERC20(tokenAddress).balanceOf(address(this)) - balanceBefore;
// use actualReceived (cast to uint128) in place of amount below
```

This ensures the emitted `amount` always equals the collateral actually held, preserving the backing invariant.

---

### Proof of Concept

1. Deploy a mock ERC20 with a configurable transfer tax (e.g., 10%).
2. Call `OmniBridge.initTransfer(mockToken, 1000, 0, 0, "alice.near", "")`.
3. Bridge receives 900 tokens (`balanceOf(bridge) == 900`).
4. `InitTransfer` event emits `amount = 1000`.
5. NEAR credits Alice with 1000 tokens.
6. Alice bridges 1000 back; `finTransfer` attempts `safeTransfer(alice_evm, 1000)` but bridge only holds 900 → reverts or drains reserves from other depositors.
7. Repeat to accumulate deficit proportional to `n * amount * tax`.

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
