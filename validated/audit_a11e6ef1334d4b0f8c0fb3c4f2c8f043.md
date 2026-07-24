### Title
Fee-on-Transfer Token Accounting Mismatch in `initTransfer` Inflates Cross-Chain Amount — (File: `evm/src/omni-bridge/contracts/OmniBridge.sol`)

### Summary
`OmniBridge.initTransfer` uses the caller-supplied `amount` parameter — not the actual post-transfer balance delta — when emitting the cross-chain `InitTransfer` event and constructing the Wormhole payload. For fee-on-transfer ERC20 tokens (e.g., USDT with fees enabled, or any deflationary token), the bridge locks fewer tokens than it claims, creating unbacked wrapped supply on NEAR and eventually making the bridge insolvent for that token.

### Finding Description
In `OmniBridge.initTransfer`, the non-bridge-token ERC20 path executes:

```solidity
IERC20(tokenAddress).safeTransferFrom(
    msg.sender,
    address(this),
    amount          // ← requested amount, not actual received
);
``` [1](#0-0) 

Immediately after, the same unverified `amount` is forwarded to `initTransferExtension` and emitted in the event:

```solidity
emit BridgeTypes.InitTransfer(
    msg.sender, tokenAddress, currentOriginNonce,
    amount,   // ← inflated, not actual received
    fee, nativeFee, recipient, message
);
``` [2](#0-1) 

In `OmniBridgeWormhole.initTransferExtension`, this same `amount` is Borsh-encoded into the Wormhole message that NEAR consumes to mint/release tokens: [3](#0-2) 

No balance-before/after check exists anywhere in the call path. The contract never measures what it actually received.

### Impact Explanation
For any fee-on-transfer ERC20 bridged through the `else` branch of `initTransfer`, the bridge locks `amount - fee_deducted` but tells NEAR to mint/release `amount`. This directly breaks the 1:1 backing guarantee. As transfers accumulate, the EVM vault becomes progressively undercollateralized. When users bridge back from NEAR to EVM, `finTransfer` attempts to `safeTransfer` the full `amount` but the vault holds less, causing the last redeemers to face a permanently unclaimable balance — an irreversible fund lock. This matches **Critical: Irreversible fund lock / permanently unclaimable user value** and **High: Balance-accounting divergence that breaks backing guarantees**.

### Likelihood Explanation
USDT's fee switch is currently off on mainnet, but the contract supports enabling it. More immediately, other fee-on-transfer tokens (e.g., STA, PAXG in certain modes, or any custom deflationary ERC20) can be bridged through this path today. The bridge imposes no whitelist on the `else` branch — any unprivileged user can call `initTransfer` with any ERC20 address. No privileged access is required.

### Recommendation
Measure the actual received amount using a balance snapshot before and after the `safeTransferFrom`, and use that delta — not the caller-supplied `amount` — for all downstream accounting, event emission, and cross-chain message construction:

```solidity
uint256 balanceBefore = IERC20(tokenAddress).balanceOf(address(this));
IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), amount);
uint256 actualReceived = IERC20(tokenAddress).balanceOf(address(this)) - balanceBefore;
// use actualReceived instead of amount going forward
```

### Proof of Concept
1. Deploy or use any ERC20 with a 1% transfer fee.
2. Call `OmniBridge.initTransfer(tokenAddress, 1000e6, 0, 0, "alice.near", "")`.
3. `safeTransferFrom` transfers 1000 tokens but the bridge receives only 990 (fee deducted).
4. The `InitTransfer` event and Wormhole message both carry `amount = 1000`.
5. NEAR mints 1000 wrapped tokens to `alice.near`.
6. Repeat N times; the vault deficit grows by 10 tokens per transfer.
7. When users bridge back, `finTransfer` calls `safeTransfer(recipient, 1000)` but the vault is short; the final redeemers cannot withdraw — funds are permanently locked.

### Citations

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L407-412)
```text
                IERC20(tokenAddress).safeTransferFrom(
                    msg.sender,
                    address(this),
                    amount
                );
            }
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L427-437)
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
    }
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
