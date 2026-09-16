### Title
Unchecked ERC20 `transfer` return value in `IntentGatewayV2.withdraw`/`onAccept` on Tron permanently freezes escrowed order funds and fee tokens - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2` redeems escrowed order tokens and protocol fees via a raw low-level `.call` to the ERC20 `transfer` selector, checking only that the call did not revert (`success`) but never decoding/validating the returned boolean. This is the same bug class as the referenced Ajna report ("Unchecked return value for transfer and transferFrom calls"), applied to Hyperbridge's cross-chain intents escrow settlement path, which is reachable by any relayer delivering a `RedeemEscrow`/`RefundEscrow` message or `SweepDust` request.

### Finding Description
In `withdraw()`, escrowed tokens are released to the beneficiary using:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
``` [1](#0-0) 

The identical unchecked pattern is used for fee-token redemption:
```solidity
(bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
if (!success) revert TransferFailed();
``` [2](#0-1) 

and for dust sweeping in `onAccept`:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
if (!success) revert TransferFailed();
``` [3](#0-2) 

`success` here only reflects whether the external call itself reverted; it does not decode the ABI-encoded `bool` return data from `transfer()`. Per the ERC20 standard (and in particular for TRC20/Tron tokens and various non-standard ERC20/TRC20 tokens deployed there), a token contract is permitted to signal a failed transfer by returning `false` rather than reverting. In that case `token.call(...)` succeeds (returns `success == true`) even though no tokens were moved.

Immediately after this unchecked "success" check, the escrow accounting is unconditionally updated:
```solidity
_orders[body.commitment][token] -= amount;
``` [4](#0-3) 
and `_filled[body.commitment] = beneficiary;` is set at function entry regardless of the actual transfer outcome: [5](#0-4) 

This is called from `onAccept`, which any relayer can trigger by delivering a proven `RedeemEscrow`/`RefundEscrow` POST request from the counterpart chain, or via `onGetResponse` after a GET response proof: [6](#0-5) [7](#0-6) 

By contrast, the canonical EVM `IntentsBase.sol`/`ExtrinsicIntents.sol` intents contracts consistently use OpenZeppelin's `SafeERC20.safeTransferFrom`/`safeTransfer`, which properly validates both call success and the returned boolean value, e.g.: [8](#0-7) 
This confirms the Tron port deviates from the safe pattern used elsewhere in the codebase and reintroduces the unchecked-return-value class of bug.

### Impact Explanation
If the escrowed input/output token or the fee token is a non-standard ERC20/TRC20 that returns `false` on failure instead of reverting (a well-known pattern on Tron and among several ERC20 implementations), the withdrawal/refund/dust-sweep will silently "succeed" from the contract's perspective:
- The beneficiary never receives the tokens.
- `_orders[body.commitment][token]` is decremented (or deleted for fees) as if payment were made, and `_filled[body.commitment]` is marked, making the order permanently unclaimable through any other path (`UnknownOrder`/`Filled` checks in other flows would now block retries).
- The tokens remain stuck in the `IntentGatewayV2` contract with no code path to recover them for that beneficiary.

This results in permanent freezing/loss of the escrowed principal and/or protocol fees for solvers and depositors, satisfying the "permanent freezing of funds" impact bar.

### Likelihood Explanation
Any relayer can deliver the proof that triggers `onAccept`, so exploitation does not require privileged access — it only requires that the order/escrow use a token whose `transfer` can return `false` without reverting. Given IntentGatewayV2 is a generic token bridge designed to support arbitrary ERC20/TRC20 tokens configured by users/solvers (not restricted to a vetted allowlist visible in this snippet), such tokens are plausible, especially on Tron/TRC20 ecosystems where non-reverting failure semantics are common.

### Recommendation
Replace all raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` unchecked-return patterns in `evm/tron/contracts/apps/IntentGatewayV2.sol` (`withdraw`, fee redemption, and `SweepDust` handling in `onAccept`) with OpenZeppelin's `SafeERC20.safeTransfer`, matching the pattern already used consistently in `evm/src/apps/intentsv2/*.sol`. This ensures both call success and the decoded boolean return value are validated, reverting the whole transaction (and leaving escrow state untouched) if the transfer truly fails.

### Proof of Concept
1. Solver/user creates a cross-chain order on the source chain using a TRC20 token `T` whose `transfer()` returns `false` on failure instead of reverting (e.g., insufficient allowance/blacklist checks implemented via return-false rather than revert).
2. Order is filled on destination; a `RedeemEscrow` message is dispatched back to the Tron `IntentGatewayV2` and delivered by a relayer with a valid proof, invoking `onAccept` → `withdraw`.
3. At the time of settlement, token `T` returns `false` for the `transfer` call to `beneficiary` (e.g., due to a paused/blacklist state on that token), but the low-level `.call` does not revert.
4. `withdraw()` treats `success == true`, decrements `_orders[body.commitment][token]`, marks `_filled[body.commitment] = beneficiary`, and emits `EscrowReleased` — despite the beneficiary receiving zero tokens.
5. The escrowed tokens remain permanently locked in `IntentGatewayV2` with no remaining code path to reclaim them for that commitment, since the order state now reflects a "filled" order and repeated calls will revert with `UnknownOrder`.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-635)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L674-675)
```text
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L692-693)
```text
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L705-708)
```text
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L710-710)
```text
            _orders[body.commitment][token] -= amount;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L719-722)
```text
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L191-196)
```text
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, totalRequired + beneficiaryShare);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }
```
