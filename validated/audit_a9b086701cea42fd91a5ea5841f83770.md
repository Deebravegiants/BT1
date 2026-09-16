### Title
Malicious order creator can escrow a poison ERC-20 alongside a legitimate token to permanently block solver payout in `IntentGatewayV2` cross-chain intents - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`placeOrder` lets a user (`order.user`) escrow an arbitrary, self-chosen list of `TokenInfo` inputs with no token allow-list or per-token isolation. When a solver later fills the order and the cross-chain `RedeemEscrow` message returns, `_withdraw()` releases *every* escrowed input token to the solver in a single atomic loop. If the user includes one legitimate token (to look attractive to solvers) alongside a malicious token engineered to always revert transfers to the solver's address (a blacklist/pausable/ERC-777-style token, analogous to the ERC777 lender in the referenced Teller report), the whole `_withdraw` call reverts every time it is attempted — permanently freezing the solver's payout while the solver has already delivered the output assets on the destination chain.

### Finding Description
`_withdraw` in `evm/src/apps/intentsv2/IntentsBase.sol` (function starting at line 451) iterates over `body.tokens` and performs a `safeTransfer` for each escrowed token to the `beneficiary` in one loop: [1](#0-0) 

There is no per-token isolation, try/catch, or ability to skip a single failing token; a single reverting `IERC20.safeTransfer` call aborts the whole function, including release of otherwise-healthy tokens and the fee-token payout that follows: [2](#0-1) 

`_withdraw` is invoked from `onAccept` for the `RedeemEscrow` message that Hyperbridge delivers back to the source chain after a solver fills the order on the destination chain: [3](#0-2) 

Order inputs are entirely user-controlled at `placeOrder` time — the user picks the escrow token list, and `_orders[commitment][token]` tracks each token's balance independently, so nothing forces the escrow set to be limited to well-behaved tokens.

Because `EvmHost.dispatchIncoming` treats a reverting `onAccept` as retryable (it deletes the request receipt so the same message can be resubmitted, rather than treating it as a permanent failure): [4](#0-3) 

...a `RedeemEscrow` message that always fails due to a poison token can be resubmitted indefinitely and will always fail identically, because the poison token's revert behavior is deterministic and controlled by the attacker (the order creator), not by any transient condition. This produces the same effect as the ERC777 lender in the Teller report: an on-chain actor uses a custom token's transfer hook to permanently block a counterparty's legitimate claim, in this case, the solver's payout — while the solver, having already delivered the output assets on the destination chain (`_fillCrossChain` transfers output tokens to the beneficiary before dispatching `RedeemEscrow`), cannot get its collateral (the escrowed input tokens) back.

### Impact Explanation
A malicious order creator can:
1. Construct an `Order` whose `inputs` include one attractive, legitimate token (e.g., USDC) and one "poison" ERC-20 they deploy that unconditionally reverts on `transfer`/`transferFrom` to any address (or specifically to addresses matching common solver patterns).
2. Have a solver fill the order cross-chain, which requires the solver to first pay out the requested `output` assets to the beneficiary on the destination chain (`_fillCrossChain`, `evm/src/apps/intentsv2/ExtrinsicIntents.sol:164-220`).
3. When the `RedeemEscrow` message returns to the source chain, `_withdraw` reverts because the poison token cannot be transferred, and it reverts on every retry.

Result: the solver is out the output tokens it delivered and can never claim the escrowed input tokens (legitimate token included), and the escrow is permanently stuck in the `IntentGatewayV2` contract for that commitment — a combination of theft (uncompensated delivery by the solver) and permanent freezing of the legitimate escrowed funds. This satisfies the "concrete theft or permanent freezing of funds" bar.

### Likelihood Explanation
Medium-to-High: any user can call `placeOrder` with arbitrary `TokenInfo[]` inputs; deploying a custom ERC-20 with a deny-list/hook that reverts against a target address is trivial and requires no special privileges. The main constraint is that a solver must be enticed to fill despite the untrusted secondary token — plausible if the primary token (e.g., a stablecoin) dominates the perceived value of the order, or if solver tooling doesn't simulate the full source-chain withdrawal path before committing to fill. This mirrors the underlying Teller root cause: pushing tokens to a counterparty-controlled or attacker-influenced address inside a state-changing settlement path without isolating failures per-asset.

### Recommendation
- In `_withdraw`, isolate each token transfer (e.g., wrap each `safeTransfer` in a low-level call with try/catch, or use a pull-based claim model) so that a single malformed/malicious token cannot block the release of the other escrowed assets or of the fee token.
- Consider maintaining per-token failure accounting (an escrow "vault" balance the beneficiary can claim later) instead of a single atomic multi-token push, so failed transfers don't corrupt the whole settlement and are not indefinitely retryable-yet-permanently-failing.
- Optionally support a solver-side token allow-list or a "self-fill" mode where solvers can flag/exclude untrustworthy tokens rather than being forced into an all-or-nothing releases.

### Proof of Concept
1. Attacker deploys `PoisonToken`, an ERC-20 whose `transfer`/`transferFrom` reverts whenever `to == <any address other than attacker>` (or specifically the expected solver address once known via `solverSelection`/EIP-712 pre-selection).
2. Attacker calls `placeOrder` with `order.inputs = [ {token: USDC, amount: 1000}, {token: PoisonToken, amount: 1} ]` and an attractive `output` (e.g., requesting less value than the USDC alone is worth), source chain A, destination chain B.
3. A solver on chain B calls `fillOrder`, delivering the requested output tokens to the beneficiary via `_fillCrossChain` (`ExtrinsicIntents.sol:191-196`), then the contract dispatches `RedeemEscrow` back to chain A.
4. On chain A, Hyperbridge relays the `RedeemEscrow` `PostRequest`; `onAccept` calls `_withdraw(body, false, true)`.
5. `_withdraw`'s loop first transfers USDC successfully, then reaches `PoisonToken.safeTransfer(solver, 1)`, which reverts — the whole `onAccept` call reverts.
6. Per `EvmHost.dispatchIncoming`, the request receipt is deleted so the message is retryable, but resubmission by any relayer produces the identical revert forever, since `PoisonToken`'s behavior never changes for that address.
7. Result: the USDC (and the poison token) remain locked in `IntentGatewayV2` forever; the solver already paid the destination-side output and receives nothing in return.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-470)
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
        }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L472-484)
```text
        if (finalize) {
            uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
            if (fees > 0) {
                delete _orders[body.commitment][TRANSACTION_FEES];
                IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
            }

            if (isRefund) {
                emit EscrowRefunded({commitment: body.commitment, tokens: body.tokens});
            } else {
                emit EscrowReleased({commitment: body.commitment, tokens: body.tokens});
            }
        }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-337)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }
```

**File:** evm/src/core/EvmHost.sol (L794-818)
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

        // replay protection
        bytes32 commitment = request.hash();
        _requestReceipts[commitment] = relayer;

        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
    }
```
