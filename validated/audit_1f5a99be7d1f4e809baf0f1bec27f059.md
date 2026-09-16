## Analysis

`CallDispatcher` is Hyperbridge's analog to Connext's `Executor` — a shared, permissionless "untrusted call" executor used by `HyperFungibleToken`, `WrappedHyperFungibleToken`, and `IntentsBase`/`IntentGatewayV2` to run attacker-supplied `Call[]` batches after tokens are minted/unlocked/delivered to it. Just like Connext's `Executor.execute`, `CallDispatcher.dispatch` performs a raw, unrestricted `to.call{value: call.value}(call.data)` to any address with any calldata, and — critically — has **no caller restriction at all**. [1](#0-0) 

Multiple apps route bridged funds through the same dispatcher before it executes attacker-controlled calls, deliberately holding tokens temporarily in the dispatcher itself: [2](#0-1) [3](#0-2) 

The docs explicitly acknowledge this residual-balance window but only recommend a best practice (exact-amount approvals) rather than enforcing it in code, and note `CallDispatcher` deployments are reused/shared across integrations: [4](#0-3) 

Unlike `HyperFungibleToken`/`WrappedHyperFungibleToken` (no sweep after `dispatch()`), `IntentsBase._execute` does sweep known output-asset balances back after dispatching, but only for the specific `order.output.assets` list — any other token or native ETH left in the dispatcher (e.g. from partial swaps, slippage, or unrelated concurrent flows) is not swept: [5](#0-4) 

Because `dispatch()` has no access control, **anyone** — not just the ISMP host or the owning app — can call `CallDispatcher.dispatch()` directly with a crafted `Call[]` (e.g. `IERC20.approve(attacker, type(uint256).max)` or `IERC20.transfer(attacker, balance)`) to sweep out any token/ETH dust that has accumulated in the shared dispatcher, exactly mirroring the Connext `Executor` bug where arbitrary calldata could grant an attacker allowance over unclaimed tokens sitting in the executor.

### Title
Unrestricted `CallDispatcher.dispatch` allows theft of any token/ETH dust left in the shared dispatcher - (File: evm/src/utils/CallDispatcher.sol)

### Summary
`CallDispatcher.dispatch()` is a public, unauthenticated function that executes arbitrary attacker-supplied `Call[]` from the dispatcher's own address. `HyperFungibleToken`, `WrappedHyperFungibleToken`, and `IntentGatewayV2`/`IntentsBase` all route bridged/escrowed tokens through this same shared contract before running attacker-controlled calldata, and can leave token or native-ETH dust behind (partial swaps, slippage, un-swept non-output tokens, or calls that don't fully spend the delivered amount). Because `dispatch()` has no caller restriction, any unprivileged actor can call it directly — without relaying any ISMP message — with calldata that grants themselves an allowance or transfers out whatever balance is sitting in the dispatcher, exactly as in the reported Connext `Executor` issue.

### Finding Description
`dispatch()` decodes an arbitrary `Call[]` and does `to.call{value: call.value}(call.data)` for each entry, with the only check being that `to` has code: [6](#0-5) . There is no `onlyHost`, `onlyApp`, or `msg.sender` check whatsoever on this external function.

Apps intentionally mint/unlock/deliver bridged tokens directly to the dispatcher address so subsequent calls in the batch can spend them:
- `HyperFungibleToken.onAccept` mints to `beneficiary` (which callers set to the dispatcher) then calls `ICallDispatcher(_dispatcher).dispatch(message.data)` with no post-dispatch sweep: [7](#0-6) 
- `WrappedHyperFungibleTokenUpgradeable.onAccept` does the same for the underlying ERC20/native token: [8](#0-7) 
- `IntentsBase._execute` dispatches order-output calldata through the same dispatcher and only sweeps the known `order.output.assets` list afterward, not arbitrary tokens/ETH: [5](#0-4) 

The docs confirm the dispatcher is meant to be a long-lived, address-stable, shared deployment reused across integrations (deployed once via `DeployHFT.s.sol`/`DeployWrappedHFT.s.sol` and referenced by address on the "contract addresses" page): [9](#0-8) , and explicitly warn that "the dispatcher contract holds tokens temporarily during execution," recommending exact-amount approvals rather than max approvals as a mitigation — i.e., acknowledging but not eliminating the residual-balance risk: [4](#0-3) 

Because a single shared `CallDispatcher` instance can be wired to many different `HyperFungibleToken`/`WrappedHyperFungibleToken` deployments and `IntentsBase`-derived gateways, any dust left by any one integration's calldata (attacker or benign sender's imperfect swap/approval sequence) is a shared, permissionlessly-drainable pool: anyone can call `dispatch()` directly with `Call({to: leftoverToken, value: 0, data: abi.encodeWithSelector(IERC20.approve.selector, attacker, type(uint256).max)})` (or a direct `transfer`) or `Call({to: attacker, value: address(dispatcher).balance, data: ""})` for stray native ETH.

### Impact Explanation
This is concrete theft of funds: any token or native-ETH balance that accumulates in the shared `CallDispatcher` — whether from slippage on a swap-then-transfer flow, a caller's calldata that doesn't fully consume minted/unlocked tokens, or a non-output token from `IntentsBase` fills — can be permissionlessly drained by any third party with no relationship to the original cross-chain message. Given the dispatcher is a shared singleton wired into potentially multiple bridge/token/intents deployments, the blast radius extends beyond a single app instance.

### Likelihood Explanation
High. No special privileges, no proof, and no cross-chain message relay is required — the attacker calls `CallDispatcher.dispatch()` directly as a normal transaction. The only precondition is that some non-zero token/ETH balance exists in the dispatcher at the time of the attack, which is a realistic and even expected outcome of composable swap/approve calldata flows the protocol explicitly documents and supports (transfer-and-swap, transfer-and-stake, etc.), where perfect balance consumption cannot be guaranteed for every third-party calldata payload.

### Recommendation
Restrict `CallDispatcher.dispatch` to be callable only by the specific app/host that is authorized to route funds through it (e.g., an `onlyAuthorizedCaller` allowlist configured per-app, or make dispatcher instances non-shared/per-app with a hard-coded owner check), and/or add a sweep step in every consumer (`HyperFungibleToken`, `WrappedHyperFungibleToken`) analogous to `IntentsBase._execute`'s sweep, generalized to sweep *any* residual balance (not just known output assets) back to the calling contract or to a designated recipient immediately after each `dispatch()` call, closing the window during which dust is drainable by an unrelated third party.

### Proof of Concept
1. A legitimate cross-chain transfer through `HyperFungibleToken.send()` sets `to = CALL_DISPATCHER` and `data` encoding a `Call[]` that approves a router for the full minted amount and swaps, but the swap only partially consumes the approved amount (e.g., due to slippage-tolerant router behavior), leaving `X` tokens sitting in `CallDispatcher`.
2. `onAccept` executes successfully: tokens are minted to the dispatcher and `ICallDispatcher(_dispatcher).dispatch(message.data)` runs the swap batch, leaving `X` residual tokens in the dispatcher (per [7](#0-6) , no sweep occurs).
3. Attacker (any address, unrelated to the transfer) calls `CallDispatcher.dispatch(abi.encode([Call({to: token, value: 0, data: abi.encodeWithSelector(IERC20.approve.selector, attacker, type(uint256).max)})]))` directly — this succeeds because `dispatch()` has no caller check ( [6](#0-5) ).
4. Attacker then calls `token.transferFrom(dispatcher, attacker, X)` using the granted allowance, draining the residual `X` tokens that belonged to the innocent bridging user's transaction dust.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L44-62)
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
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-313)
```text
    function onAccept(IncomingPostRequest calldata incoming) public virtual override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }

        emit Received({
            from: message.from,
            to: beneficiary,
            source: string(request.source),
            amount: message.amount
        });
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L338-357)
```text
        if (_isWeth) {
            // Try a native-ETH push first (cheap for EOAs and payable contracts);
            // if the recipient cannot accept native value (no `receive()` / `fallback()
            // payable`), re-wrap the withdrawn ETH and deliver the underlying WETH as
            // an ERC-20 transfer instead. This mirrors the deposit-side flexibility of
            // `send()` (which accepts WETH from non-payable callers via `safeTransferFrom`)
            // so the refund path doesn't permanently lock funds for the same caller class.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = beneficiary.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(beneficiary, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-98)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
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

**File:** evm/script/DeployHFT.s.sol (L9-26)
```text
contract DeployHFT is BaseScript {
    function deploy() internal override {
        string memory name = vm.envString("HFT_NAME");
        string memory symbol = vm.envString("HFT_SYMBOL");

        CallDispatcher dispatcher = new CallDispatcher{salt: salt}();
        HyperFungibleToken hft = new HyperFungibleToken{salt: salt}(name, symbol, admin);

        hft.configure(HyperFungibleToken.ConfigOptions({
            host: HOST_ADDRESS,
            dispatcher: address(dispatcher)
        }));

        vm.stopBroadcast();
        console.log("=== HFT Deployment ===");
        console.log("HyperFungibleToken:", address(hft));
        console.log("CallDispatcher:", address(dispatcher));
    }
```
