### Title
Fee-on-Transfer Token Accounting Divergence in `initTransfer` Creates Unbacked Cross-Chain Supply — (`evm/src/omni-bridge/contracts/OmniBridge.sol`)

### Summary

`OmniBridge.initTransfer()` accepts an arbitrary ERC20 token and records the caller-supplied `amount` in the `InitTransfer` event without verifying the actual balance received. For fee-on-transfer (FoT) tokens, the bridge vault receives less than `amount`, but the event—consumed by the NEAR relayer to credit the destination chain—encodes the full `amount`. This creates unbacked wrapped supply on the destination chain and permanently undercollateralizes the EVM vault.

### Finding Description

In `OmniBridge.initTransfer()`, when the token is neither a bridge-deployed token nor a custom-minter token, the contract executes a plain `safeTransferFrom` and then emits `InitTransfer` with the caller-supplied `amount`:

```solidity
// OmniBridge.sol lines 406–412
IERC20(tokenAddress).safeTransferFrom(
    msg.sender,
    address(this),
    amount
);
```

```solidity
// OmniBridge.sol lines 427–436
emit BridgeTypes.InitTransfer(
    msg.sender,
    tokenAddress,
    currentOriginNonce,
    amount,   // ← user-supplied, not actual received amount
    fee,
    nativeFee,
    recipient,
    message
);
```

For a FoT token, `safeTransferFrom` deducts a fee in-flight, so `address(this)` receives `amount - fot_fee`. The emitted event still carries `amount`. The NEAR bridge relayer reads this event and calls `fin_transfer` on NEAR (or another destination chain) for the full `amount`, minting or releasing `amount` tokens. The EVM vault is now short by `fot_fee` per transfer.

The same structural issue exists in `OmniBridgeWormhole.initTransferExtension()`, which publishes the caller-supplied `amount` into the Wormhole VAA payload without any balance-before/after check.

### Impact Explanation

Every `initTransfer` call with a FoT token inflates the destination-chain supply relative to the EVM collateral. Over time, the vault becomes progressively undercollateralized. When users bridge tokens back via `finTransfer`, the EVM bridge attempts `safeTransfer(recipient, amount)` from its vault; the last redeemers find insufficient balance and their redemptions revert permanently. This satisfies two allowed impact categories:

- **Critical — Irreversible fund lock**: the last cohort of users holding destination-chain wrapped tokens can never redeem them because the EVM vault is drained before their `finTransfer` executes.
- **High — Asset-accounting divergence**: the total wrapped supply on the destination chain exceeds the locked collateral on EVM, breaking the 1:1 backing guarantee.

### Likelihood Explanation

FoT tokens (e.g., PAXG, STA, tokens with deflationary mechanics) are standard ERC20 tokens. Any unprivileged user can call `initTransfer` with such a token. No privileged role, leaked key, or external compromise is required. The bridge does not whitelist tokens, so any registered or unregistered ERC20 can be supplied. The attacker does not need to act maliciously—ordinary users bridging a FoT token trigger the accounting error automatically.

### Recommendation

Measure the actual balance received using a before/after balance check and use that delta—not the caller-supplied `amount`—in the emitted event:

```solidity
uint256 balanceBefore = IERC20(tokenAddress).balanceOf(address(this));
IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), amount);
uint256 balanceAfter = IERC20(tokenAddress).balanceOf(address(this));
uint128 actualReceived = uint128(balanceAfter - balanceBefore);
// use actualReceived in place of amount for the event and cross-chain message
```

Alternatively, document that FoT/rebasing tokens are explicitly unsupported and add a token allowlist enforced on-chain.

### Proof of Concept

1. Deploy or identify a FoT ERC20 token `T` that charges a 1% fee on every transfer. Register it with the bridge (or use it directly as a non-bridge-token path).
2. Call `OmniBridge.initTransfer(T, 1000, 0, 0, "recipient.near", "")`.
3. Inside `initTransfer`, `safeTransferFrom(msg.sender, address(this), 1000)` executes; the bridge receives 990 tokens (1% fee deducted).
4. `emit InitTransfer(..., 1000, ...)` fires with `amount = 1000`.
5. The NEAR relayer picks up the event and calls `fin_transfer` on NEAR for 1000 tokens; NEAR mints 1000 wrapped-T to the recipient.
6. Repeat N times. The EVM vault holds `990 * N` tokens; the NEAR supply is `1000 * N`.
7. The first `990 * N / 1000` users who bridge back successfully redeem. The remaining users' `finTransfer` calls on EVM revert with insufficient balance—their wrapped tokens are permanently frozen.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2)

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

**File:** evm/src/omni-bridge/contracts/OmniBridgeWormhole.sol (L118-150)
```text
    function initTransferExtension(
        address sender,
        address tokenAddress,
        uint64 originNonce,
        uint128 amount,
        uint128 fee,
        uint128 nativeFee,
        string calldata recipient,
        string calldata message,
        uint256 value
    ) internal override {
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
        // slither-disable-next-line reentrancy-eth
        _wormhole.publishMessage{value: value}(
            wormholeNonce,
            payload,
            _consistencyLevel
        );

        wormholeNonce++;
    }
```
