## Title
Missing ERC20 return-value check in `withdraw()`/`SweepDust` allows silent transfer failures and permanent loss of escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` releases escrowed tokens using a raw low-level `.call()` with the `IERC20.transfer` selector, and only checks that the *call itself* did not revert. It never decodes/validates the boolean return value that `transfer()` is supposed to produce. This is precisely the class of bug the SafeERC20 audit finding warns about, but here it manifests in the opposite direction from the original report: instead of failing on tokens with no return value, the code blindly accepts tokens that return `false` on failure as if the transfer succeeded, permanently losing escrowed funds.

### Finding Description
In `withdraw()` and the `SweepDust` branch of `onAccept()`, token payouts are performed like this: [1](#0-0) 

```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
```

`success` here only reflects whether the external call reverted — it says nothing about the ABI-encoded `bool` that `transfer()` returns. Any ERC20 implementation that returns `false` instead of reverting on failure (e.g., paused/blacklist-aware tokens, some deflationary tokens, or a token intentionally crafted to always return `false`) will make this call "succeed" from the contract's point of view even though no tokens moved.

Immediately after this unchecked call, the contract permanently commits the effects of a (falsely) successful transfer: [2](#0-1) 

- `_filled[body.commitment] = beneficiary` is set, finalizing the order.
- `_orders[body.commitment][token] -= amount` deletes the escrow accounting for that token.

The same unchecked pattern is used for protocol dust sweeps and fee redemption: [3](#0-2) [4](#0-3) 

By contrast, the primary EVM implementation of the same protocol correctly uses `SafeERC20.safeTransfer`, which validates the boolean return value (or the absence of one) via OpenZeppelin's `Address.functionCall` + return-data checks: [5](#0-4) 

The Tron variant's use of raw `.call()` plus a manual selector, without validating the returned boolean, reintroduces exactly the risk the SafeERC20 fix was meant to eliminate — except worse, since it doesn't even attempt to decode a returned `false`.

### Impact Explanation
This is reachable from a normal, unprivileged relayer submitting a valid cross-chain settlement message: `onAccept()` handles `RequestKind.RedeemEscrow`/`RefundEscrow` by calling `withdraw()` after routine `authenticate()`, and `SweepDust` after the standard hyperbridge-source check. If the escrowed token silently returns `false` on transfer for any reason (blacklisting the gateway/beneficiary, token paused, custom "soft-fail" token logic), the contract will:
1. Report the transfer as successful.
2. Mark the order `_filled`, preventing any retry or alternate settlement path.
3. Zero out the escrow accounting (`_orders[...] -= amount`).

The beneficiary receives nothing, and because `_filled`/`_orders` state is already finalized, the tokens sitting in the contract become permanently unreachable through the intended withdrawal flow. This is a direct freezing/loss of user or solver funds in the intents escrow settlement path.

### Likelihood Explanation
Requires an ERC20 token (input/output asset of an order) whose `transfer()` can return `false` instead of reverting on failure. Such tokens exist in practice (blacklist/pausable tokens, and adversarial tokens designed specifically to grief escrow contracts). The protocol already anticipates and tests non-standard token behavior (fee-on-transfer tokens are explicitly handled elsewhere), indicating orders using non-standard ERC20s are an expected use case, making this a realistic occurrence rather than a purely theoretical one. No privileged role or governance action is needed — only a normal relayer delivering a legitimate settlement message for an order that used such a token.

### Recommendation
Replace all raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `evm/tron/contracts/apps/IntentGatewayV2.sol` (in `withdraw()`, the `SweepDust` handler, and the fee-redemption call) with `SafeERC20.safeTransfer`, matching the pattern already used correctly in `evm/src/apps/intentsv2/IntentsBase.sol`. This ensures both call-revert failures and boolean-`false` failures are treated as failures and revert the transaction instead of finalizing escrow state.

### Proof of Concept
1. Deploy a malicious/non-standard ERC20 token whose `transfer()` returns `false` when the recipient is blacklisted (or unconditionally returns `false` after a certain condition) instead of reverting.
2. A user places an order on the Tron `IntentGatewayV2` using this token as an input asset; tokens are escrowed via `safeTransferFrom` (still correctly guarded on the deposit side).
3. A solver fills the order; Hyperbridge relays a valid `RedeemEscrow` `PostRequest` to the source chain.
4. `onAccept()` → `withdraw()` executes `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))`; the token's `transfer()` returns `false` but does not revert, so `success == true`.
5. `_orders[commitment][token]` is decremented to zero and `_filled[commitment]` is set, finalizing the order — yet `beneficiary` never received the tokens, which remain stuck in the `IntentGatewayV2` contract with no code path left to recover them.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L673-681)
```text
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
                unchecked {
                    ++i;
                }
                emit DustSwept(token, amount, req.beneficiary);
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-723)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

        // redeem escrowed tokens
        uint256 len = body.tokens.length;
        for (uint256 i; i < len;) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
            unchecked {
                ++i;
            }
        }

        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-469)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
