### Title
Unaccounted-for reward/side tokens left stranded in the shared `CallDispatcher` during predispatch/postdispatch execution — ([File: evm/src/apps/IntentGatewayV2.sol], [File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
The Intent Gateway's `predispatch` (order placement) and `postdispatch` (`_execute`, run on fill) flows route arbitrary calldata through a single, persistent, shared `CallDispatcher` contract, then "sweep" only the specific tokens that are declared in `order.inputs` (predispatch) or `order.output.assets` (postdispatch) back to the gateway. Any other token balance the arbitrary call happens to produce — e.g. a farming/staking reward token, an airdrop, or leftover dust from an intermediate swap hop that isn't one of the enumerated order tokens — is never collected and remains stuck in the shared `CallDispatcher`, exactly analogous to the reported ICHI issue where `wIchiFarm.burn` returns both LP tokens and ICHI rewards, but only the LP tokens are re-deposited/collected while the ICHI rewards are left in the spell contract.

### Finding Description
In `placeOrder`, when `order.predispatch.call.length > 0`, predispatch assets are transferred to the shared dispatcher (`_params.dispatcher`), the untrusted call is executed via `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)`, and then the gateway builds sweep calls **only for the tokens listed in `order.inputs`**: [1](#0-0) 

Balances of any token not in `order.inputs` that the predispatch call produced (e.g., harvested rewards from an unwrap/farm-exit style call) are never measured or swept — they simply remain on the `dispatcher` contract: [2](#0-1) 

The same pattern exists on the fill side. `_execute` in `IntentsBase.sol`, which runs the order's `output.call` (postdispatch) after a fill, sweeps dust **only for `order.output.assets[i].token`**: [3](#0-2) 

Critically, the `CallDispatcher` is not a fresh, single-use, or ephemeral contract per call — it is a single shared, persistent contract address stored in `_params.dispatcher` and reused by every order that carries predispatch/postdispatch calldata: [4](#0-3) 

Because the dispatcher is shared across all users and orders, any token balance stranded there by one order's predispatch/postdispatch execution (mirroring the ICHI report's "harvested rewards left in the spell contract") sits available to be claimed by *any subsequent transaction* that happens to route that token through the dispatcher (e.g., an attacker crafts an order whose `predispatch`/`postdispatch` call sweeps that exact token as part of its own enumerated `order.inputs`/`order.output.assets`, or directly calls the dispatcher to move the token out to themselves since `dispatch()` performs no ownership/authorization checks on the calls it executes). This is a stronger version of the ICHI bug because the "spell contract" analog here is explicitly shared infrastructure, not a private per-user vault.

### Impact Explanation
Funds (arbitrary ERC-20 reward/side tokens produced by predispatch/postdispatch calldata routed through DeFi protocols, staking/farming contracts, DEX aggregators, etc.) are permanently unaccounted for by the protocol and can be extracted by any unprivileged third party who submits a follow-up order or calldata batch that references the CallDispatcher and the stranded token, or via a direct arbitrary call to `CallDispatcher.dispatch` transferring the token out (since `dispatch` has no access control and executes any `Call[]` supplied by the caller). This is a concrete theft/loss-of-funds vector reachable by any unprivileged user who can call `placeOrder`/`fillOrder` with calldata, satisfying the "unbacked/lost funds, exploitable by unprivileged actor" bar for a valid analog. Severity is High, matching the source report's rating, because the shared nature of `CallDispatcher` widens the blast radius beyond a single user's position.

### Likelihood Explanation
Likelihood is Medium-to-High: it requires an order to use predispatch/postdispatch calldata that routes through a protocol producing an incidental token not enumerated in `order.inputs`/`order.output.assets` (common for LP unwraps, farm exits, auto-compounding vaults, or DEX routes with intermediate reward tokens), and requires an attacker/relayer/solver to notice the balance and craft a follow-up call to `CallDispatcher.dispatch` (a public, unauthenticated function) to extract it. Both preconditions are realistic given the documented use cases for predispatch/postdispatch calldata (swap-then-escrow, fill-then-act, DeFi composability).

### Recommendation
- Change the sweep logic in both `placeOrder`'s predispatch flow (`IntentGatewayV2.sol`) and `_execute`'s postdispatch flow (`IntentsBase.sol`) to sweep **the full token surface actually touched or held by the dispatcher after the call**, not just the tokens declared in `order.inputs`/`order.output.assets`. Options: require the predispatch/postdispatch call to declare all tokens it may produce (and validate this against a per-call allowlist), or add a generic `sweepAll(address[] tokens)` step, similar to the `SweepDust` request kind already implemented in `evm/tron/contracts/apps/IntentGatewayV2.sol`, that lets governance/relayers reclaim any residual balance from the shared dispatcher for any token, and emit `DustCollected`/`DustSwept` for all of it.
- Alternatively, deploy or `CREATE2` a fresh, single-use `CallDispatcher` per order execution so that no cross-order token contamination or accumulation of unclaimed balances is possible, closing the "shared spell contract" attack surface entirely.
- Restrict `CallDispatcher.dispatch` so it cannot be invoked directly by arbitrary EOAs to drain stray token balances (e.g., gate it to only the configured `IntentGatewayV2` instance), which limits (but does not fully fix) the exploitability of any token that does get stranded.

### Proof of Concept
1. Governance/deployer configures `_params.dispatcher` to a single shared `CallDispatcher` instance used by all orders (as done today per `evm/src/apps/IntentGatewayV2.sol` line 236, `address dispatcher = _params.dispatcher;`).
2. User A places an order with `predispatch.call` that unwraps an LP/vault position through the dispatcher, yielding both the expected `order.inputs` token and an unrelated reward token R (mirroring the ICHI `wIchiFarm.burn` return of both LP tokens and ICHI rewards).
3. `placeOrder`'s sweep logic (`evm/src/apps/IntentGatewayV2.sol` lines 260–311) only builds `transferCalls` for `order.inputs` tokens; token R's balance on the dispatcher is never measured or moved, and stays on `CallDispatcher`.
4. Because `CallDispatcher.dispatch` (`evm/src/utils/CallDispatcher.sol` lines 44–62) is public and unauthenticated, Attacker B calls `CallDispatcher.dispatch(abi.encode([Call({to: R, value: 0, data: transfer(B, balance)})]))` directly, or crafts their own `placeOrder`/`fillOrder` with `predispatch`/`postdispatch` referencing token R as one of their own `order.inputs`/`order.output.assets`, causing the gateway's own sweep logic to credit R's stranded balance to Attacker B's order instead of User A.
5. User A's harvested reward token R is permanently lost to the protocol/user and captured by an unrelated third party — the same loss-of-funds outcome described in the source ICHI report.

(Note: I was unable to fully confirm within the available context whether the non-Tron `evm/src/apps/IntentGatewayV2.sol`/`IntentsBase.sol` codepath has an equivalent `SweepDust`-style generic recovery mechanism reachable by governance elsewhere in the file, since the Tron variant (`evm/tron/contracts/apps/IntentGatewayV2.sol`) does implement a `SweepDust` request kind at lines 661–682 that the main EVM version does not appear to expose in the sections reviewed. If such a mechanism exists elsewhere in the main EVM contract, the practical loss window is bounded to the period before that sweep is executed, though the fundamental "swept-fields are token-list-scoped, not balance-agnostic" root cause still stands.)

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L258-282)
```text
            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);

            // Build sweep calls and snapshot gateway balances before the sweep.
            Call[] memory transferCalls = new Call[](inputsLen);
            uint256[] memory balancesBefore = new uint256[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;

                if (token == address(0)) {
                    uint256 balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                    balancesBefore[i] = address(this).balance;
                } else {
                    uint256 balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    balancesBefore[i] = IERC20(token).balanceOf(address(this));
                }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L291-311)
```text
            // Measure actual received, emit dust for excess, update order.inputs.
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }

                if (received > order.inputs[i].amount) {
                    uint256 dust = received - order.inputs[i].amount;
                    emit DustCollected(token, dust);
                } else {
                    order.inputs[i].amount = received;
                }

                unchecked {
                    ++i;
                }
            }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-533)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

        Call[] memory sweepCalls = new Call[](outputsLen);
        uint256 sweepCount = 0;

        for (uint256 i; i < outputsLen;) {
            address token = address(uint160(uint256(order.output.assets[i].token)));

            if (token == address(0)) {
                uint256 balance = dispatcher.balance;
                if (balance > 0) {
                    sweepCalls[sweepCount] = Call({to: address(this), value: balance, data: ""});
                    sweepCount++;
                    emit DustCollected(token, balance);
                }
            } else {
                uint256 balance = IERC20(token).balanceOf(dispatcher);
                if (balance > 0) {
                    sweepCalls[sweepCount] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    sweepCount++;
                    emit DustCollected(token, balance);
                }
            }

            unchecked {
                ++i;
            }
        }
```

**File:** evm/src/utils/CallDispatcher.sol (L25-62)
```text
contract CallDispatcher is ICallDispatcher {
    /**
     * @dev error thrown when the target is not a contract.
     */
    error NotContract(address target);

    /**
     * @dev error thrown when a call fails.
     */
    error CallFailed(address target, bytes result);

    /**
     * @dev Receive function to accept ETH transfers
     */
    receive() external payable {}

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
    }
```
