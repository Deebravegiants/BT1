### Title
Raw low-level `.call()` to token addresses without contract-existence check in `withdraw()`/dust-sweep lets settlement silently "succeed" without transferring funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of the Intent Gateway (`evm/tron/contracts/apps/IntentGatewayV2.sol`) departs from the pattern used everywhere else in the codebase for calling out to token/asset addresses. Elsewhere (`CallDispatcher.sol`, `EvmHost.dispatchIncoming`) the code explicitly checks `extcodesize` before performing a low-level `.call()` and reverts (`NotContract`) if the target has no code. `withdraw()` and the `SweepDust` handler in the Tron `IntentGatewayV2` instead do a bare `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only check the boolean `success`, with no code-existence check.

### Finding Description
`withdraw()` (lines ~691-730) escrow-release logic: [1](#0-0) 
and the `SweepDust` handler in `onAccept` (governance path): [2](#0-1) 

both call `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` and treat `success == true` as proof of a completed transfer, decrementing `_orders[body.commitment][token]` and emitting `EscrowReleased`/`EscrowRefunded` regardless. On the EVM (non-Tron) side, the exact same operation instead uses OpenZeppelin's `SafeERC20.safeTransfer`, which internally verifies the target has code before treating the call as successful: [3](#0-2) 

The protocol's own security pattern for exactly this class of risk — "external call to a possibly-empty/unverified address should not be trusted blindly" — is demonstrated by `CallDispatcher.dispatch`, which explicitly guards with an `extcodesize` check and reverts with `NotContract` before making the call: [4](#0-3) 
and by `EvmHost.dispatchIncoming`, which likewise checks `extcodesize` before invoking the destination module: [5](#0-4) 

The Tron `IntentGatewayV2.withdraw()`/`SweepDust` path breaks this invariant: a low-level `.call()` to an address with no deployed code (e.g., a token whose contract has been destroyed, an address that never had code, or one on an intermediate/incorrect chain) returns `success = true` with empty return data — Solidity's low-level call semantics do not distinguish "no code, so nothing ran" from "ran and returned nothing." The function has no way to detect this and proceeds as if funds were transferred.

### Impact Explanation
This is directly analogous to the external report's core concern — the code trusts an external call to an address without verifying the callee is a genuine, expected contract, and treats a no-op interaction as success. Concretely:
- `withdraw()` is invoked from the ISMP `onAccept` settlement path (`RedeemEscrow`/`RefundEscrow`) when a relayer delivers a cross-chain settlement message, and from `onGetResponse` for source-chain cancellation refunds. If the escrowed token's code is unavailable at call time, the contract marks the order filled/refunded, deletes fee escrow, and emits the success event — but the beneficiary receives nothing. The escrowed balance bookkeeping (`_orders[commitment][token]`) is decremented as though funds moved, permanently orphaning the value with no path to retry (the order is already marked filled/refunded).
- The same missing guard applies to `SweepDust`, a Hyperbridge-governance-triggered path, compounding the risk that protocol dust sweeps can silently fail without any revert/alarm.

This meets the "permanent freezing of funds" / "unauthorized app action" bar: state that should gate value release instead finalizes without releasing it, and there is no retry mechanism once `_filled`/`_orders` state is updated.

### Likelihood Explanation
Likelihood depends on the escrowed token's bytecode remaining present between escrow and settlement. On post EIP-6780 EVM (Ethereum), `SELFDESTRUCT` mid-life is effectively impossible outside of same-transaction construction, making it hard to independently invalidate deployed token code on mainnet EVM chains. However, this file specifically targets Tron/TVM, where `SUICIDE`/self-destruct and contract lifecycle semantics differ from post-Cancun EVM and are less constrained; TRC20 tokens or intermediary contracts destroyed or not yet deployed at settlement time are plausible on that target chain. Given the explicit engineering effort elsewhere in the same codebase to guard this exact failure mode (`CallDispatcher`, `EvmHost.dispatchIncoming`), the omission here looks like an inconsistency introduced when porting the EVM contract to Tron rather than an intentional design choice, but I could not verify Tron-specific self-destruct semantics or additional upstream validation (e.g., during order placement) within the available index, so likelihood should be treated as uncertain pending further chain-specific verification.

### Recommendation
Route all outbound token transfers in the Tron `IntentGatewayV2.withdraw()` and `SweepDust` handler through `SafeERC20.safeTransfer` (already imported and used elsewhere via `using SafeERC20 for IERC20`) instead of raw `.call()`, or explicitly perform the same `extcodesize` check used in `CallDispatcher.sol` and `EvmHost.dispatchIncoming` before treating a `.call()` as successful. Any zero-code target should revert rather than silently succeed.

### Proof of Concept
Conceptual outline (could not be executed against the codebase in this environment):
1. Place a cross-chain order on the source chain whose input token is a contract that can later end up with no deployed code at the destination-chain settlement address that the withdraw path resolves to (e.g., a not-yet-deployed or destroyed TRC20 on Tron).
2. Solver fills the order on the destination chain; a `RedeemEscrow` message is relayed back to the Tron `IntentGatewayV2`.
3. `onAccept` → `withdraw()` executes `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` against the now-codeless address; the call returns `success = true` trivially.
4. `_orders[commitment][token]` is decremented, `_filled[commitment]` is set, and `EscrowReleased` is emitted — but the beneficiary never receives the tokens, and the order cannot be retried since it is already marked filled.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-682)
```text
        } else if (kind == RequestKind.SweepDust) {
            SweepDust memory req = abi.decode(incoming.request.body[1:], (SweepDust));

            uint256 outputsLen = req.outputs.length;
            for (uint256 i; i < outputsLen;) {
                TokenInfo memory info = req.outputs[i];
                address token = address(uint160(uint256(info.token)));
                uint256 amount = info.amount;

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-469)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```

**File:** evm/src/utils/CallDispatcher.sol (L41-61)
```text
    /**
     *  @dev reverts if the target is not a contract or if any of the calls reverts.
     */
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

**File:** evm/src/core/EvmHost.sol (L794-803)
```text
    function dispatchIncoming(PostRequest memory request, address relayer) external restrict(_hostParams.handler) {
        address destination = _bytesToAddress(request.to);
        uint256 size;
        assembly {
            size := extcodesize(destination)
        }
        if (size == 0) {
            // instead of reverting the entire batch, early return here.
            return;
        }
```
