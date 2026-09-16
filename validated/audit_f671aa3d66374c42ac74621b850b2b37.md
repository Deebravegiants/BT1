## Title
Unrestricted `CallDispatcher.dispatch()` allows any address to trigger "trusted" cross-chain call execution, draining residual token approvals and native ETH left in the dispatcher - (File: evm/src/utils/CallDispatcher.sol)

## Summary
`CallDispatcher.dispatch()` is `external` with **no access control** — any address can invoke it, not just `HyperFungibleToken`/`WrappedHyperFungibleToken` `onAccept` callbacks. The contract is a shared, canonically-deployed singleton used by multiple bridge apps, is `payable`, and by design temporarily holds ERC-20 approvals and native ETH mid-execution of the `Call[]` sequence dispatched from a cross-chain message. Because the entry point that executes this "trusted" call sequence is not gated to the legitimate caller (the token contract's `onAccept`), the same execution primitive that was meant to be reachable only through a verified ISMP delivery is directly reachable by any unprivileged party — mirroring CVE-2024-3044's core defect (a trusted-only execution path becoming reachable without the expected trust check).

## Finding Description
`CallDispatcher.dispatch(bytes memory encoded)` decodes a `Call[]` and executes each entry with `to.call{value: call.value}(call.data)` in the dispatcher's own storage/msg.sender context: [1](#0-0) 

There is no modifier restricting the caller (e.g., no `onlyHFT`, `onlyHost`, or allow-list of authorized token contracts). Compare this with every other execution surface in the ISMP apps, all of which are explicitly gated by `onlyHost`: [2](#0-1) 

`HyperFungibleToken.onAccept` (and its Upgradeable/Wrapped variants) forward the message's embedded `Call[]` payload straight to this unrestricted `dispatch()`: [3](#0-2) 

The documented design explicitly acknowledges that the dispatcher can be left holding value across calls, and instructs users to limit allowances only as a mitigation of a known residue risk — it does not close it: [4](#0-3) 

Because `dispatch()` is public and unauthenticated, once *any* legitimate `onAccept` execution leaves the `CallDispatcher` holding:
- an ERC-20 allowance that a downstream router/protocol did not fully consume (e.g., slippage-limited swaps, partial fills, or an allowance intentionally sized larger than what the last hop in the `Call[]` actually pulls), or
- native ETH forwarded via `Call.value` that a downstream call did not fully spend (the contract's `receive()` accepts arbitrary ETH and has no withdrawal function restricted to an owner)

...any external address can call `CallDispatcher.dispatch()` directly with its own `Call[]` to sweep that residual allowance or ETH balance to an address of its choosing. The "trusted script" (the `Call[]` execution engine) that was only supposed to be reachable via a verified ISMP `onAccept` delivery is in fact reachable by anyone at any time.

## Impact Explanation
This results in concrete theft of funds: any token approval or native ETH left over in the shared `CallDispatcher` (which is deployed once and reused across multiple `HyperFungibleToken`/`WrappedHyperFungibleToken` deployments per the contract-addresses documentation) can be drained by an unprivileged attacker who is not part of any ISMP message flow. Given the dispatcher is a canonical, address-stable, shared component across many bridge deployments and integrations that route swaps/stakes/deposits through it, the residual-approval/ETH attack surface accumulates across every integration built on top of it.

## Likelihood Explanation
Likelihood is high in practice for integrations that (a) approve router allowances sized generously to tolerate slippage rather than exact output amounts (the docs themselves flag "unlimited allowances" as a foreseeable misuse, implying non-exact allowances occur), or (b) forward `Call.value` amounts that a downstream call doesn't fully consume. Any attacker monitoring on-chain `Received`/`CallDispatcher` activity can trivially detect leftover approvals/ETH and immediately submit their own `dispatch()` call to claim them — no special privileges, timing races with the legitimate relayer, or proof forgery are required.

## Recommendation
Restrict `CallDispatcher.dispatch()` to only be callable by authorized/registered caller contracts (e.g., an allow-list of HFT/WHFT deployments set at deploy time, or by making the dispatcher single-use/ephemeral per delivery via `CREATE2`/minimal proxy pattern), and/or ensure the dispatcher never retains value across transactions (e.g., forcibly zero out any granted allowances and sweep back any unspent native value to the mint/unlock beneficiary at the end of `dispatch()`).

## Proof of Concept
1. A legitimate cross-chain transfer with calldata mints/unlocks tokens to the `CallDispatcher` and instructs it to `approve` a DEX router for `amount` then perform a `swapExactTokensForTokens` with `minAmountOut < amount` (per the documented usage pattern) — the router only pulls what it needs to hit `minAmountOut`, leaving a residual allowance from the `CallDispatcher` to the router, and/or leftover token balance sitting in the `CallDispatcher` from a partially-filled Call.value ETH swap.
2. `onAccept` completes successfully (revert-free), so the residual allowance/leftover balance persists in the shared `CallDispatcher` contract.
3. Any external address (no relationship to the bridge, no ISMP proof) calls `CallDispatcher.dispatch(encodedCalls)` directly — this is unauthenticated per [5](#0-4)  — with a `Call[]` that calls `transferFrom(callDispatcher, attacker, residualAllowance)` on the router-approved token, or that simply captures any ETH balance still held by the dispatcher.
4. The attacker's calls succeed because the dispatcher performs no origin check, draining value that legitimate users/bridged funds left behind.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L39-62)
```text
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

**File:** sdk/packages/core/contracts/apps/HyperApp.sol (L129-131)
```text
    function onAccept(IncomingPostRequest calldata) external virtual onlyHost {
        revert UnexpectedCall();
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L301-305)
```text
        _mint(beneficiary, message.amount);

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
