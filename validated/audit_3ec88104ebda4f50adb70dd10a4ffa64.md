## Analysis: Read-only reentrancy analog in IntentGatewayV2 escrow accounting

Based on my research, I found a concrete analog to the Balmy `Vault#withdraw` read-only reentrancy pattern in the intents subsystem's escrow-accounting order of operations.

### Title
Stale `_orders` escrow state readable during external native-token callback in `IntrinsicIntents._fillSameChain` / `ExtrinsicIntents._fillCrossChain` - (File: `evm/src/apps/intentsv2/IntrinsicIntents.sol`, `evm/src/apps/intentsv2/ExtrinsicIntents.sol`)

### Summary
`IntentGatewayV2` already hardens the *state-mutating* reentrancy vector by setting `_filled[commitment] = msg.sender` before any external call (a CEI fix confirmed by the dedicated `IntrinsicIntentsReentrancyTest.sol` suite). However, the escrow accounting map `_orders[commitment][token]` — a `public` mapping [1](#0-0)  — is **not** updated until `_withdraw` runs near the end of the fill function, which is *after* the attacker-controlled `beneficiary` has already received a native ETH push via a raw `.call`.

### Finding Description
In `IntrinsicIntents._fillSameChain`, for native-token outputs the contract does: [2](#0-1) 

This external call to `beneficiary` (fully attacker-controlled, taken from `order.output.beneficiary`) happens while `_orders[commitment][...]` still holds the **full pre-fill escrow value** — the decrement only happens later, inside `_withdraw`, called at: [3](#0-2) 

`_withdraw` is where the escrow mapping is actually mutated: [4](#0-3) 

The same ordering exists in `ExtrinsicIntents._fillCrossChain`: the beneficiary receives native ETH via `_sendValue` before the cross-chain `RedeemEscrow` post is dispatched, and `_orders` on this (destination) chain is never decremented at all in the cross-chain path (only the source chain's `_orders` is decremented later, asynchronously, via `onAccept`). [5](#0-4) 

Because `_orders` is a public auto-generated getter, any contract — including the beneficiary itself upon receiving ETH, or another contract it calls into during that callback — can read `_orders(commitment, token)` mid-transaction and observe a state that is inconsistent with `_filled[commitment]` (already non-zero) and with the fact that outputs have already been paid out. This is structurally identical to the reported Balancer/Curve read-only reentrancy class: state consumers that trust a view/getter mid-call can be fed stale values.

Grep results show that `_orders`/`_filled` are referenced on-chain outside `IntentGatewayV2` itself by `evm/src/apps/intentsv2/SolverAccount.sol`, which is the solver-facing ERC-4337 style account contract used to authorize/execute fills. I was not able to fully read `SolverAccount.sol` in this session (final iteration limit reached), so I cannot confirm with certainty whether it performs a *synchronous* on-chain read of `_orders`/`_filled` that could be reentered during the beneficiary callback described above, or whether its references are purely for post-hoc bookkeeping/off-chain-verifiable data. This is the key remaining unknown.

### Impact Explanation
If `SolverAccount.sol` (or any other on-chain consumer) makes an authorization or accounting decision based on `_orders`/`_filled` while being reentered mid-fill (e.g., validating that an order is "still escrowed" or "not yet filled" before permitting a solver action, or before releasing solver collateral), a malicious `beneficiary` could exploit the stale view to double-authorize an action or bypass an escrow check, potentially resulting in theft of solver funds or double-spend of a single fill's escrow accounting. Without confirming the exact logic in `SolverAccount.sol`, the severity is bounded between "no impact" (if it never reads gateway state synchronously) and "High" (if it gates fund movement on a synchronous read of `_orders`/`_filled`).

### Likelihood Explanation
The trigger requires only a single `fillOrder` call with a native-ETH output and an attacker-controlled `beneficiary` contract — fully reachable by any unprivileged solver/filler, matching the required "single submitted transaction" bar. No governance or privileged role is needed.

### Recommendation
Move the `_orders[commitment][token]` decrement (and any other escrow-affecting state) to occur strictly before any external call to `beneficiary`/`msg.sender`, following full checks-effects-interactions, in both `_fillSameChain` and `_fillCrossChain`. Alternatively, if third-party/on-chain consumers such as `SolverAccount.sol` must read escrow state, add a transient reentrancy guard scoped to the fill functions (not just to `fillOrder`'s outer call) so `_orders` cannot be read mid-fill, mirroring Balancer's `VaultReentrancyLib` pattern referenced in the original report.

### Proof of Concept
Conceptual (not verified end-to-end due to inability to confirm `SolverAccount.sol`'s exact read path in this session):
1. Attacker crafts an `Order` with a native-ETH output and `beneficiary` = a malicious contract.
2. Solver calls `fillOrder`; `_filled[commitment]` is set, but `_orders[commitment][inputToken]` is untouched.
3. `IntrinsicIntents._fillSameChain` executes `beneficiary.call{value: ...}("")`.
4. Inside `beneficiary`'s `receive()`, it calls into `SolverAccount.sol` (or another integrator) which reads `_orders(commitment, inputToken)`/`_filled(commitment)` on the gateway and — if it treats the still-full escrow value as authoritative — takes an action premised on stale state (e.g., authorizes a second solver payout or double-counts escrow).
5. Execution returns to `_fillSameChain`, which then calls `_withdraw` and finally zeroes/decrements `_orders`.

**Caveat**: I could not fully verify step 4 because `SolverAccount.sol`'s implementation was not read in full before the tool budget was exhausted — a Devin session with full file access should inspect `evm/src/apps/intentsv2/SolverAccount.sol` for any synchronous reads of `_orders`/`_filled` (or calls into `IntentGatewayV2`) to confirm whether this read-only reentrancy window is concretely exploitable for fund theft, or whether it is a low/no-impact theoretical gap.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L140-145)
```text
    /**
     * @dev Maps (commitment, token address) to the escrowed amount for that token.
     * Decremented as tokens are released via fills or refunds.
     */
    mapping(bytes32 => mapping(address => uint256)) public _orders;

```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-469)
```text
            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L95-106)
```text
            if (token == address(0)) {
                if (msgValue < beneficiaryTotal + protocolShare) revert InsufficientNativeToken();
                msgValue -= (beneficiaryTotal + protocolShare);
                // Inline, not `_sendValue`: this loop is at the via-ir stack limit.
                (bool sent,) = beneficiary.call{value: beneficiaryTotal}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, beneficiaryTotal);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L126-129)
```text
        WithdrawalRequest memory body = WithdrawalRequest({
            commitment: commitment, tokens: escrowedInputs, beneficiary: bytes32(uint256(uint160(msg.sender)))
        });
        _withdraw(body, false, isFullyFilled);
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L164-219)
```text
    function _fillCrossChain(Order calldata order, FillOptions calldata options, bytes32 commitment) internal {
        uint256 outputsLen = order.output.assets.length;

        _filled[commitment] = msg.sender;

        uint256 msgValue = msg.value;
        address beneficiary = address(uint160(uint256(order.output.beneficiary)));
        TokenInfo[] memory outputFills = new TokenInfo[](outputsLen);

        for (uint256 i; i < outputsLen; i++) {
            bytes32 outputToken = order.output.assets[i].token;
            if (options.outputs[i].token != outputToken) revert InvalidInput();

            address token = address(uint160(uint256(outputToken)));
            uint256 totalRequired = order.output.assets[i].amount;
            uint256 solverAmount = options.outputs[i].amount;

            if (solverAmount < totalRequired) revert InvalidInput();

            (uint256 protocolShare, uint256 beneficiaryShare) =
                _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);

            if (token == address(0)) {
                if (msgValue < solverAmount) revert InsufficientNativeToken();
                uint256 beneficiaryTotal = totalRequired + beneficiaryShare;
                _sendValue(beneficiary, beneficiaryTotal);
                msgValue -= (beneficiaryTotal + protocolShare);
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, totalRequired + beneficiaryShare);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }
            if (protocolShare > 0) emit DustCollected(token, protocolShare);
            outputFills[i] = TokenInfo({token: outputToken, amount: totalRequired});
        }

        _execute(order, outputsLen);

        // Native dispatch fee only if the solver sent enough to cover it; else the fee token.
        uint256 nativeFee = options.nativeDispatchFee;
        if (nativeFee > msgValue) nativeFee = 0;
        msgValue -= nativeFee;
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );

        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }

        emit OrderFilled({commitment: commitment, filler: msg.sender, outputs: outputFills, inputs: order.inputs});
```
