Found the analog: the `withdraw()` function in the Tron variant of `IntentGatewayV2` checks only whether the low-level `call` succeeded (didn't revert), but never inspects the returned ABI-encoded boolean from `transfer()`. This is the exact bug class from the report (unchecked ERC20 return value) reachable from an unprivileged relayer/solver flow, since `withdraw()` is invoked from `onAccept()` for `RedeemEscrow`/`RefundEscrow` messages (triggered by anyone relaying a valid cross-chain proof) and from `onGetResponse()` for GET-request based refunds.

### Title
Unchecked ERC20 `transfer()` return value lets escrow withdrawals silently "succeed" without moving funds - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.withdraw()` releases escrowed input tokens and transaction fees to a solver/user by making a raw low-level `call` to `IERC20.transfer.selector` and only checking that the call did not revert (`success`), never decoding/validating the returned `bool`. Non-standard ERC20 tokens that return `false` on failure instead of reverting will make this function treat a failed transfer as successful. [1](#0-0) 

### Finding Description
`withdraw()` is the internal function that releases escrowed order inputs and protocol fees once a settlement or refund message is accepted. For every non-native token it does:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
``` [2](#0-1) 
and the identical pattern for fee-token payout: [3](#0-2) 

`success` here only reflects whether the target contract's code executed without reverting (i.e., the call reached and returned from the token contract). It says nothing about the encoded `bool` return value that ERC20's `transfer()` is supposed to return to signal success/failure. Some ERC20 implementations (e.g., tokens that follow the historically common "return false on failure" pattern rather than reverting) will cause this `call` to return `success = true` with return data encoding `false`, meaning the transfer was rejected internally (e.g., insufficient balance in an edge-case, blacklist, paused state) yet the gateway proceeds as if the beneficiary was paid.

Critically, right after the (possibly failed) transfer, the code unconditionally decrements internal escrow accounting:
```solidity
_orders[body.commitment][token] -= amount;
``` [4](#0-3) 
and marks the order as filled/refunded via `_filled[body.commitment] = beneficiary;` at the top of the function [5](#0-4) . Because the order is marked filled and escrow accounting is decremented regardless of whether tokens actually left the contract, a false-returning token transfer permanently strands the escrowed funds inside the `IntentGateway` contract — they can never be re-claimed because the commitment is already recorded as settled and the internal balance is already zeroed out.

This path is reachable by any relayer submitting a valid cross-chain proof for a `RedeemEscrow`/`RefundEscrow` request (the settlement content itself, i.e. which token/beneficiary/amount, is determined by the solver's `fillOrder` call on the destination chain and dispatched cross-chain — not by governance), making it part of the unprivileged intents/escrow settlement flow rather than an admin-only code path. `onAccept()` dispatches to `withdraw()` for these kinds: [6](#0-5) , and `onGetResponse()` also calls `withdraw()` for GET-based refunds: [7](#0-6) .

The `SweepDust` handling in the same contract has the identical unchecked-return pattern [8](#0-7) , but that path is gated by `keccak256(incoming.request.source) != keccak256(hyperbridge())` (governance-only), so it is out of scope per the exclusion of malicious-governance paths; `withdraw()` is not gated this way and is the in-scope analog.

Note: the mainline EVM `IntentGatewayV2.sol` (non-Tron) consistently uses OpenZeppelin's `SafeERC20.safeTransfer`/`safeTransferFrom` for input escrow and predispatch flows [9](#0-8) , so this defect appears specific to the Tron fork of the contract at `evm/tron/contracts/apps/IntentGatewayV2.sol`, which reimplements token transfers using raw low-level calls instead of `SafeERC20`.

### Impact Explanation
If any escrowed input token or the fee token used by an order is a non-reverting ERC20 (returns `false` instead of reverting on failure), a legitimate settlement/refund can be processed by the gateway (order marked filled, internal escrow balance decremented, `EscrowReleased`/`EscrowRefunded` event emitted) while the beneficiary receives nothing. The tokens remain locked in the `IntentGateway` contract with no recovery path, since the commitment is already marked as filled and cannot be re-withdrawn. This is a permanent freezing/loss of user and solver funds.

### Likelihood Explanation
Likelihood depends on whether a non-reverting ERC20 is used as an input asset or the configured fee token; many real-world tokens (and any custom/blacklist/pausable-with-boolean-failure tokens) exhibit this behavior. Since users and solvers choose the tokens involved in an order at `placeOrder`/`fillOrder` time, and the fee token is a protocol-wide configuration parameter, exposure is plausible whenever the deployment supports non-standard ERC20s, which is a realistic condition for a general-purpose cross-chain intents gateway.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw()` (and the `SweepDust` handler) with OpenZeppelin's `SafeERC20.safeTransfer`, matching the approach already used in the mainline `evm/src/apps/IntentGatewayV2.sol` contract. `safeTransfer` reverts on both call failure and a `false` boolean return, ensuring escrow accounting and `_filled` state are never updated unless the transfer actually succeeded.

### Proof of Concept
1. Deploy a token whose `transfer()` returns `false` (instead of reverting) when, e.g., the recipient is blacklisted or the internal transfer condition fails, while still returning `true` under normal conditions (a broad class of legacy/non-standard ERC20s).
2. A user places an order on the Tron `IntentGatewayV2` with this token as an input asset; a solver fills the order cross-chain.
3. When the settlement `RedeemEscrow` message is relayed back and `onAccept()` → `withdraw()` executes, engineer the token so `transfer()` internally returns `false` for the beneficiary (e.g., beneficiary temporarily blacklisted at settlement time).
4. `withdraw()` observes `success == true` (call didn't revert) and proceeds: `_filled[commitment] = beneficiary`, `_orders[commitment][token] -= amount`, and emits `EscrowReleased`.
5. The beneficiary's token balance is unchanged — the escrowed tokens remain trapped in the `IntentGatewayV2` contract, and because the order is already marked filled, there is no code path to retry or reclaim the funds. [10](#0-9)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-635)
```text
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L673-676)
```text
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L249-251)
```text
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }
```
