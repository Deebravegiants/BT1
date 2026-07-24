### Title
Fee-on-Transfer Token Accounting Divergence Creates Unbacked Wrapped Supply on NEAR - (File: `evm/src/omni-bridge/contracts/OmniBridge.sol`)

### Summary
In `OmniBridge.initTransfer`, when a native ERC20 token (not a bridge token, not a custom minter) is locked, the contract calls `safeTransferFrom` for the user-specified `amount` and then emits `InitTransfer` with that same `amount`. If the token charges a transfer fee, the bridge receives less than `amount`, but the NEAR side processes the event and credits the full `amount` — creating unbacked wrapped supply and eventual insolvency on redemption.

### Finding Description

In `OmniBridge.initTransfer`, the non-bridge-token ERC20 path locks tokens into the contract: [1](#0-0) 

After this `safeTransferFrom`, the function passes the original user-supplied `amount` — not the actual balance delta — to `initTransferExtension` and emits it in the `InitTransfer` event: [2](#0-1) 

`SafeERC20.safeTransferFrom` only checks that the call does not revert and that the return value (if any) is `true`. It does **not** verify that the contract's balance increased by exactly `amount`. For fee-on-transfer tokens (e.g., USDT with fees enabled, PAXG, STA, etc.), the bridge receives `amount - fee` but the `InitTransfer` event records `amount`. The NEAR-side bridge listener reads this event and mints/credits the full `amount` of wrapped tokens to the recipient.

### Impact Explanation

This creates a direct backing shortfall: the EVM bridge holds `amount - fee` of the native token, but the NEAR side has minted `amount` of wrapped tokens. Every subsequent `initTransfer` with a fee-on-transfer token widens the deficit. When wrapped-token holders bridge back via `finTransfer`, the bridge will eventually be unable to release the full collateral, causing:

- **Unbacked wrapped supply** on NEAR (breaks backing guarantee — fits "balance-accounting divergence that breaks backing guarantees").
- **Irreversible fund lock / permanently unclaimable value** for late redeemers once the bridge's native token reserve is exhausted.

This is a Critical/High impact under the allowed scope.

### Likelihood Explanation

Any unprivileged user can call `initTransfer` with a fee-on-transfer ERC20 token address. No privileged role is required. The token just needs to be a non-bridge, non-custom-minter ERC20 that the bridge has not explicitly blocked. The bridge has no token allowlist for the native-lock path, so any such token is accepted.

### Recommendation

After the `safeTransferFrom` call, measure the actual balance delta and use that as the credited amount:

```solidity
uint256 balanceBefore = IERC20(tokenAddress).balanceOf(address(this));
IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), amount);
uint256 received = IERC20(tokenAddress).balanceOf(address(this)) - balanceBefore;
require(received == amount, "fee-on-transfer token not supported");
```

Either enforce exact receipt (rejecting fee-on-transfer tokens) or propagate `received` instead of `amount` through the rest of the function so the NEAR side is credited only what was actually locked.

### Proof of Concept

1. Alice calls `initTransfer(feeToken, 1000, 0, 0, "alice.near", "")` where `feeToken` charges a 1% transfer fee.
2. `safeTransferFrom` moves 1000 tokens from Alice; the bridge receives 990 (10 taken as fee).
3. `InitTransfer` event is emitted with `amount = 1000`.
4. NEAR bridge listener processes the event and mints 1000 wrapped `feeToken` to `alice.near`.
5. Alice (or any holder) later calls `finTransfer` on NEAR to bridge 1000 back to EVM.
6. The EVM bridge attempts `safeTransfer(recipient, 1000)` but only holds 990, causing a revert — funds are permanently locked for that user.
7. Repeated deposits widen the deficit until the bridge is insolvent. [3](#0-2)

### Citations

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L373-437)
```text
    function initTransfer(
        address tokenAddress,
        uint128 amount,
        uint128 fee,
        uint128 nativeFee,
        string calldata recipient,
        string calldata message
    ) external payable whenNotPaused(PAUSED_INIT_TRANSFER) {
        currentOriginNonce += 1;
        if (fee >= amount) {
            revert InvalidFee();
        }

        uint256 extensionValue;
        if (tokenAddress == address(0)) {
            if (fee != 0) {
                revert InvalidFee();
            }
            extensionValue = msg.value - amount - nativeFee;
        } else {
            extensionValue = msg.value - nativeFee;
            if (customMinters[tokenAddress] != address(0)) {
                IERC20(tokenAddress).safeTransferFrom(
                    msg.sender,
                    customMinters[tokenAddress],
                    amount
                );
                ICustomMinter(customMinters[tokenAddress]).burn(
                    tokenAddress,
                    amount
                );
            } else if (isBridgeToken[tokenAddress]) {
                BridgeToken(tokenAddress).burn(msg.sender, amount);
            } else {
                IERC20(tokenAddress).safeTransferFrom(
                    msg.sender,
                    address(this),
                    amount
                );
            }
        }

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
    }
```
