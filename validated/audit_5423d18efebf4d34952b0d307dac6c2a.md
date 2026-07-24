### Title
Deflationary ERC20 Token Transfer in `initTransfer` Credits Full `amount` Despite Receiving Less — (`File: evm/src/omni-bridge/contracts/OmniBridge.sol`)

---

### Summary

`OmniBridge.initTransfer` locks native ERC20 tokens by calling `safeTransferFrom(msg.sender, address(this), amount)` and then unconditionally propagates the caller-supplied `amount` to the cross-chain message. For fee-on-transfer (deflationary) ERC20 tokens the contract receives strictly less than `amount`, yet the destination chain credits the full `amount`, creating unbacked wrapped supply and eventually making the bridge insolvent for honest users.

---

### Finding Description

In `OmniBridge.initTransfer`, the `else` branch for plain ERC20 tokens performs:

```solidity
IERC20(tokenAddress).safeTransferFrom(
    msg.sender,
    address(this),
    amount          // ← caller-controlled, not verified against actual receipt
);
``` [1](#0-0) 

Immediately after, the unmodified `amount` is forwarded to `initTransferExtension` and emitted in the `InitTransfer` event:

```solidity
initTransferExtension(
    msg.sender, tokenAddress, currentOriginNonce,
    amount,   // ← original, not actual-received
    ...
);
emit BridgeTypes.InitTransfer(..., amount, ...);
``` [2](#0-1) 

In `OmniBridgeWormhole`, `initTransferExtension` encodes this same `amount` into the Wormhole VAA payload:

```solidity
Borsh.encodeUint128(amount),   // ← inflated amount published cross-chain
``` [3](#0-2) 

The NEAR bridge reads this VAA and credits the full `amount` to the recipient on NEAR. No balance-before/balance-after check exists anywhere in the EVM lock path to detect the shortfall.

---

### Impact Explanation

Every `initTransfer` of a deflationary token creates a deficit: the EVM vault holds `amount − transfer_fee` but the NEAR side mints `amount`. The deficit accumulates with each such transfer. When users later bridge back (NEAR → EVM `finTransfer`), the vault cannot release the full amounts owed, causing honest users to receive less than they deposited or to be permanently blocked — a direct backing-guarantee break and irreversible fund loss for other depositors.

This falls squarely within:
- **Critical** — unbacked wrapped supply created through normal settlement flow.
- **Critical** — irreversible fund lock / permanently unclaimable value for other bridge users.

---

### Likelihood Explanation

`logMetadata` is a permissionless, payable function callable by any address for any ERC20 token. [4](#0-3) 

Once a deflationary token's metadata is logged and the NEAR-side deployment is completed (requiring MPC signing, but that is a standard operational step for any new token), any unprivileged user can call `initTransfer` with that token. Fee-on-transfer tokens are common in production (e.g., tokens with auto-liquidity or reflection mechanics). No special role or leaked key is required — the attacker only needs to call the public `initTransfer` entry point.

---

### Recommendation

Measure the actual received amount using a balance snapshot before and after the transfer, and use the delta — not the caller-supplied `amount` — for all downstream accounting and cross-chain message encoding:

```solidity
uint256 balanceBefore = IERC20(tokenAddress).balanceOf(address(this));
IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), amount);
uint256 actualReceived = IERC20(tokenAddress).balanceOf(address(this)) - balanceBefore;
// use actualReceived in place of amount for initTransferExtension and event emission
```

Alternatively, explicitly document and enforce (via an allowlist or on-chain check) that only non-deflationary tokens may be bridged through the native-lock path.

---

### Proof of Concept

1. A fee-on-transfer ERC20 token `FOT` (2% burn on every transfer) is registered with the bridge via `logMetadata` + NEAR-side deployment.
2. Attacker calls `initTransfer(FOT, 1000e18, 0, 0, "near:attacker.near", "")`.
3. `safeTransferFrom` moves `1000e18` from attacker; FOT's internal hook burns 2%, so the bridge vault receives `980e18`.
4. `initTransferExtension` encodes `amount = 1000e18` into the Wormhole VAA.
5. NEAR bridge processes the VAA and mints `1000e18` wrapped FOT to `attacker.near`.
6. Attacker now holds `1000e18` wrapped FOT on NEAR backed by only `980e18` in the EVM vault.
7. Repeated over many transfers, the vault deficit grows. When honest users attempt to bridge back, `finTransfer` releases tokens from the vault; the last users to redeem find the vault short and cannot recover their full principal.

### Citations

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L224-232)
```text
    function logMetadata(address tokenAddress) external payable {
        string memory name = IERC20Metadata(tokenAddress).name();
        string memory symbol = IERC20Metadata(tokenAddress).symbol();
        uint8 decimals = IERC20Metadata(tokenAddress).decimals();

        logMetadataExtension(tokenAddress, name, symbol, decimals);

        emit BridgeTypes.LogMetadata(tokenAddress, name, symbol, decimals);
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

**File:** evm/src/omni-bridge/contracts/OmniBridgeWormhole.sol (L136-136)
```text
            Borsh.encodeUint128(amount),
```
