## Analysis

The QuickSwap `safeTransfer` bug — a low-level `.call()` to a token that treats a "success" from a destroyed/non-existent contract as a real transfer — has a direct analog in Hyperbridge's Tron-specific intents contract.

### Where [1](#0-0) 

`withdraw()` releases escrowed order funds to a beneficiary. For every non-native token it performs:

```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
_orders[body.commitment][token] -= amount;
``` [2](#0-1) 

This is different from the main EVM `IntentGatewayV2.sol`, which uses OpenZeppelin's `SafeERC20.safeTransfer`/`safeTransferFrom` (`using SafeERC20 for IERC20`) throughout the escrow flow, e.g. in `_withdraw` in `IntentsBase.sol`: [3](#0-2) 

OZ's `SafeERC20` internally relies on `Address.functionCall`, which reverts when the target has no code — protecting against exactly the "destroyed/non-existent contract returns default success" issue described in the report. The Tron contract's raw `token.call(...)` in `withdraw` (and the same pattern in `onAccept`'s `SweepDust` handling and fee redemption) has **none of these protections**: no `extcodesize` check, and — unlike the original QuickSwap `TransferHelper.safeTransfer` — it doesn't even check `data.length == 0 || abi.decode(data, (bool))`; it only checks the raw `success` boolean: [4](#0-3) 

Contrast this with the `CallDispatcher.sol` used elsewhere in the codebase, which explicitly guards against this class of bug via `extcodesize`: [5](#0-4) 

### Reachability

`withdraw()` is reached from multiple externally-triggerable, unprivileged paths:
- `onAccept` for `RedeemEscrow`/`RefundEscrow` — delivered by any relayer submitting a valid cross-chain POST request proof: [6](#0-5) 
- `onGetResponse` after a storage-proof query (any relayer can submit the proof once dispatched): [7](#0-6) 
- `cancelOrder` on the same chain, callable by the order owner: [8](#0-7) 

Because the token used as an order input is fully attacker/user-chosen (`order.inputs[i].token`, arbitrary address), and no allowlist of tokens is enforced in `placeOrder`, an order can escrow a token that either (a) is later self-destructed like in the original PoC, or (b) is a non-reverting ERC20 that returns `false` on transfer failure (a broader and more directly reachable trigger than self-destruct, since standard non-reverting ERC20s like USDT-style tokens exist). In either case, `withdraw`'s bare `if (!success) revert` will not catch the failure: the low-level `.call` succeeds (EVM design for calls to accounts with no code, or the token contract catching the failure internally and returning `false` without reverting), `_orders[...][token] -= amount` proceeds, and `_filled[body.commitment] = beneficiary` marks the order permanently settled — while the beneficiary never actually receives the token. Since there is no fallback/retry path once `_filled` is set, the escrowed balance becomes permanently stuck/unredeemable, matching the "permanent freezing of funds" impact criterion.

---

### Title
Unsafe raw `.call` for ERC20 transfers in `IntentGatewayV2.withdraw` (Tron) fails to detect non-existent/non-standard tokens, permanently freezing escrowed funds - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2` implements token payouts with a raw low-level `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` instead of OpenZeppelin's `SafeERC20`, used everywhere else in the codebase. This raw call only checks the boolean `success` return of the low-level call, not contract code existence nor the ERC20 return-data semantics, exactly mirroring the QuickSwap `TransferHelper.safeTransfer` flaw.

### Finding Description
In `withdraw()`, `onAccept`'s `SweepDust` branch, and the transaction-fee redemption path of `evm/tron/contracts/apps/IntentGatewayV2.sol`, ERC20 payouts are performed via:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
```
A `.call` to an address with no bytecode (e.g., a self-destructed ERC20) returns `success == true` by EVM design, and a legitimate but non-standard ERC20 (returning `false` instead of reverting on failure) will also make `success == true` even though the actual transfer failed, since the check never inspects the returned `data`. In both cases the code proceeds as if the transfer succeeded: it decrements `_orders[commitment][token]` and, for `withdraw`, sets `_filled[commitment] = beneficiary`, permanently marking the order as settled.

### Impact Explanation
Once `_filled[commitment]` is set, there is no retry mechanism to reclaim escrowed tokens for that commitment. If the escrowed token is destroyed post-creation, or is a token whose `transfer` can return `false` without reverting, the beneficiary permanently loses access to the escrowed amount even though the contract's internal accounting treats the order as fulfilled — a permanent freezing (and effective loss) of user funds. This affects the `RedeemEscrow`/`RefundEscrow` flows reachable by any relayer submitting a valid cross-chain proof, `SweepDust` protocol operations, and the transaction-fee redemption path.

### Likelihood Explanation
Order tokens are arbitrary, user-supplied addresses at `placeOrder` time with no allowlisting, so the vulnerable code path is reachable in normal cross-chain intent settlement flows. Triggering it does not require a privileged actor — any order creator can select a non-standard/self-destructible token as an input, and any relayer delivering the corresponding valid proof will drive execution into `withdraw`.

### Recommendation
Replace the raw `.call` pattern in `withdraw`, the `SweepDust` handler, and the fee-redemption block with OpenZeppelin's `SafeERC20.safeTransfer` (already imported and used via `using SafeERC20 for IERC20` in this same file for `safeTransferFrom` elsewhere), which both validates target contract code existence and correctly decodes the ERC20 return value, consistent with the rest of the codebase (e.g. `evm/src/apps/intentsv2/IntentsBase.sol`).

### Proof of Concept
1. A user places an order via `placeOrder` whose `order.inputs` includes a custom ERC20 token `T` that either self-destructs post-creation or implements `transfer` to return `false` on failure instead of reverting.
2. The order is filled/cancelled and a `RedeemEscrow`/`RefundEscrow` POST request (or GET response) is relayed to this contract.
3. `onAccept`/`onGetResponse` invoke `withdraw(body, ...)`.
4. `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` returns `success = true` despite no actual token transfer taking place (no code at `token`, or `transfer` returning `false`).
5. `_orders[commitment][token] -= amount` and `_filled[commitment] = beneficiary` execute, permanently marking the order filled; the beneficiary never receives the escrowed tokens and has no path to reclaim them.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L516-539)
```text
    function cancelOrder(Order calldata order, CancelOptions calldata options) public payable {
        bytes32 commitment = keccak256(abi.encode(order));

        // order has already been filled
        if (_filled[commitment] != address(0)) revert Filled();

        address hostAddr = host();
        bytes32 currentChain = keccak256(IDispatcher(hostAddr).host());
        bytes32 orderSource = keccak256(order.source);
        bytes32 orderDest = keccak256(order.destination);
        bool isSameChain = orderSource == orderDest;

        if (isSameChain) {
            // Same-chain: validate locally and refund immediately
            // only owner can cancel
            if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

            // Verify we're on the correct chain
            if (orderSource != currentChain) revert WrongChain();

            WithdrawalRequest memory body =
                WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user});

            withdraw(body, true);
```

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L670-681)
```text
                if (token == address(0)) {
                    (bool sent,) = req.beneficiary.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-730)
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

        if (isRefund) {
            emit EscrowRefunded({commitment: body.commitment});
        } else {
            emit EscrowReleased({commitment: body.commitment});
        }
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L465-469)
```text
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```

**File:** evm/src/utils/CallDispatcher.sol (L44-61)
```text
    function dispatch(bytes memory encoded) external {
        Call[] memory calls = abi.decode(encoded, (Call[]));
        uint256 callsLen = calls.length;
        for (uint256 i = 0; i < callsLen; ++i) {
            Call memory call = calls[i];
            uint32 size;
            address to = call.to;
            assembly {
                size := extcodesize(to)
            }

            if (size == 0) {
                revert NotContract(to);
            }

            (bool success, bytes memory result) = to.call{value: call.value}(call.data);
            if (!success) revert CallFailed(to, result);
        }
```
