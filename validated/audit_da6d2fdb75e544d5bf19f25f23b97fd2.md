This is a valid, strong analog. `CallDispatcher.dispatch()` has zero access control, and the deployment is a single shared singleton reused across `IntentGatewayV2`, `HyperFungibleToken`, and `WrappedHyperFungibleToken` on every chain — one address (e.g. `0xE2C7e576E26E0bE7aC97c6fE925bcDAbD87c4bEd` on mainnet) permanently listed on the public contract-addresses page. Combined with the fact that legitimate order/calldata flows routinely leave the dispatcher with `type(uint256).max` ERC20 approvals to well-known routers (exactly the pattern the docs themselves warn against for HFT but that the shipped `IntentGatewayV2Test.sol` postdispatch example actually uses), this reproduces the DODO "infinite approve + attacker-controlled external call" bug class, but the attack surface here is even wider because no `swapTarget` restriction or user-specific state is required at all — anyone can invoke `dispatch()` directly.

### Title
Unrestricted `CallDispatcher.dispatch()` combined with standing infinite ERC20 approvals allows anyone to drain dust/leftover/mistakenly-sent tokens - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch(bytes)` has no access control (no `onlyOwner`/`onlyGateway`/`onlyHost` modifier) and can be called by any externally owned account or contract, executing an arbitrary `Call[]` from the dispatcher's own context. [1](#0-0) 
This is the same shared, address-stable contract used by `IntentGatewayV2` for predispatch/postdispatch order calldata and by `HyperFungibleToken`/`WrappedHyperFungibleToken` for cross-chain calldata execution, on every EVM chain. [2](#0-1) 

### Finding Description
Standard order fulfillment flows through `IntentGatewayV2` set `approve(router, type(uint256).max)` from the `CallDispatcher` to routers such as Uniswap V2, as shown in the shipped test suite's own postdispatch pattern: [3](#0-2) 
The docs even flag this pattern as risky for the HFT calldata-execution path, recommending exact-amount approvals "since the dispatcher contract holds tokens temporarily during execution" — but that recommendation is advisory only; nothing in `CallDispatcher.sol` enforces it, and nothing prevents the approval from outliving the order it was granted for. [4](#0-3) 

Once a standing max allowance exists from the `CallDispatcher` to a router, any attacker can call `dispatch()` directly (it is a public, unrestricted external function) with a `Call[]` targeting that router — e.g. `swapExactTokensForTokens` or `transferFrom`-based calls — to pull any ERC20 balance the dispatcher happens to be holding at that moment and route it to an attacker-controlled address. The dispatcher's `receive()` also accepts arbitrary ETH. [5](#0-4) 

The report's "leftover fund" precondition (mistaken transfers, airdrops, dust from swaps, fee-on-transfer token rounding) applies identically here: the dispatcher is a long-lived, publicly known address that is documented and indexed, exactly the profile of the DODO route-proxy addresses cited in the original report as accumulating unexpected leftover balances. Unlike the DODO case — where the attacker still had to route through a specific `swapTarget`/`approveTarget` pairing enforced by the router itself — here there is no restriction at all on who may invoke `dispatch()`, so an attacker doesn't need to construct any indirection through the intent-fill flow; a single direct call suffices.

### Impact Explanation
Any token balance the `CallDispatcher` accumulates — from dust rounding in predispatch/postdispatch swaps, fee-on-transfer token slippage, accidental direct transfers, or airdrops to the well-known indexed address — combined with any standing infinite approval left by a prior legitimate order's calldata, is stealable by any unprivileged caller. This is a direct, permanent theft-of-funds vector on a shared, cross-app singleton contract deployed identically across every EVM chain Hyperbridge supports.

### Likelihood Explanation
High. The precondition (a standing max approval to a known router) is not a hypothetical misuse — it is the exact pattern demonstrated in the project's own test suite for realistic postdispatch swap flows, and `dispatch()`'s complete lack of access control is unconditional and always present, requiring no misconfiguration to exploit.

### Recommendation
- Restrict `CallDispatcher.dispatch()` to be callable only by an authorized caller (e.g., the `IntentGatewayV2`/HFT contract that owns the current in-flight order, via a transient-storage-gated authorization similar to the `select`/`fillOrder` pattern already used elsewhere in the codebase), or deploy a fresh, single-use `CallDispatcher` per call context instead of a shared singleton.
- Never grant unlimited (`type(uint256).max`) approvals from the dispatcher; approve only the exact amount needed for each call, and revoke/reset the allowance to zero after use.
- Add a post-dispatch invariant check that reverts if the dispatcher retains any non-zero allowance to any contract touched during the call batch.

### Proof of Concept
1. A user places an `IntentGatewayV2` order whose `output.call` performs an exact-output Uniswap V2 swap using `type(uint256).max` as `amountInMax` and pre-approves the router for `type(uint256).max`, mirroring `testPostdispatchTokenSweep` in the test suite. [6](#0-5) 
2. This grants a standing, unbounded allowance from the shared `CallDispatcher` to the Uniswap router that is never revoked after the order completes.
3. At any later point, if the `CallDispatcher` holds any balance of that token (dust from a subsequent unrelated order's fee-on-transfer transfer, an accidental transfer to the indexed public address, or an airdrop), an attacker calls `CallDispatcher.dispatch()` directly with a `Call[]` invoking the router's swap function specifying itself as recipient and using the standing allowance — no `onlyHost`/`onlyGateway` check exists to stop this. [7](#0-6) 
4. The router's `transferFrom(dispatcher, ...)` succeeds using the pre-existing max allowance, and the attacker receives the swapped-out tokens, draining the dispatcher's balance.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L36-62)
```text
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

**File:** docs/content/developers/evm/contract-addresses/mainnet.mdx (L19-23)
```text
| `UniswapV2 (UniV3 Wrapper)` | [`0x98B0eDd13ff99c40A453b88d308C4B21a3Ad0EAc`](https://etherscan.io/address/0x98B0eDd13ff99c40A453b88d308C4B21a3Ad0EAc) |
| `TokenGateway (Deprecated)` | [`0xFd413e3AFe560182C4471F4d143A96d3e259B6dE`](https://etherscan.io/address/0xFd413e3AFe560182C4471F4d143A96d3e259B6dE) |
| `CallDispatcher` | [`0xE2C7e576E26E0bE7aC97c6fE925bcDAbD87c4bEd`](https://etherscan.io/address/0xE2C7e576E26E0bE7aC97c6fE925bcDAbD87c4bEd) |
| `IntentGatewayV2` | [`0xAe041F7B0CB581876832830baeB6a2Aa2a3C9716`](https://etherscan.io/address/0xAe041F7B0CB581876832830baeB6a2Aa2a3C9716) |
| `IntentGatewayV2 (Implementation)` | [`0x9d82B05156d0da273D66C5cCbDccef2b00EE06A7`](https://etherscan.io/address/0x9d82B05156d0da273D66C5cCbDccef2b00EE06A7) |
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L1358-1377)
```text
        // Call 1: Approve Uniswap router
        postdispatchCalls[0] = Call({
            to: address(usdc),
            value: 0,
            data: abi.encodeWithSelector(IERC20.approve.selector, uniswapRouter, type(uint256).max)
        });

        // Call 2: Exact output swap - swap USDC for exactly 1000 DAI
        postdispatchCalls[1] = Call({
            to: uniswapRouter,
            value: 0,
            data: abi.encodeWithSelector(
                bytes4(keccak256("swapTokensForExactTokens(uint256,uint256,address[],address,uint256)")),
                daiOutputAmount, // exact amount out
                type(uint256).max, // max amount in
                path,
                address(dispatcher), // tokens come back to dispatcher
                block.timestamp
            )
        });
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-98)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
```
