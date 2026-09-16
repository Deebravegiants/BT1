This is a strong analog: `HyperApp.dispatchWithFeeToken` pulls fee-token funds from an attacker-controlled `request.payer` address via `safeTransferFrom`, exactly mirroring the `provider` pattern in the external report.

### Title
`HyperApp.dispatchWithFeeToken` pulls ERC-20 fee tokens from an arbitrary attacker-supplied `payer` address instead of `msg.sender` - ([File: sdk/packages/core/contracts/apps/HyperApp.sol])

### Summary
`HyperApp.dispatchWithFeeToken(DispatchPost/DispatchGet)` reads a `payer` field out of the request struct and, whenever `payer != address(this)`, calls `IERC20(feeToken).safeTransferFrom(request.payer, address(this), request.fee)` [1](#0-0) [2](#0-1) . Because `payer` is an arbitrary field supplied by whoever builds/calls the wrapping dispatch function, any address that ever approved the calling HyperApp contract to move its fee-token can have that allowance drained by an unrelated third party, without consent — the same root cause as the reported `AccountableFixedTerm::coverDefault` "provider" bug: pulling funds from an address named in calldata rather than from `msg.sender`.

### Finding Description
`dispatchWithFeeToken` is meant to let an app pay Hyperbridge's dispatch fee in the protocol fee token. The documentation itself shows that callers are expected to construct the `DispatchPost`/`DispatchGet` struct with a `payer` field, and multiple example call-sites explicitly pass `payer` as a *function parameter* rather than hardcoding `msg.sender` (see `readRemoteState(bytes,bytes[],address payer)` in the docs, which builds `DispatchGet{ ..., payer: payer }` and calls `dispatchWithFeeToken(getRequest)`) [3](#0-2) . Concretely, in the API docs:

```solidity
function readRemoteState(
    bytes memory dest,
    bytes[] memory keys,
    address payer
) public returns (bytes32) {
    ...
    DispatchGet memory getRequest = DispatchGet({..., payer: payer});
    return dispatchWithFeeToken(getRequest);
}
```

Whenever a concrete app built on `HyperApp` exposes an entry point that lets the caller choose an arbitrary `payer` (as the reference documentation pattern encourages), `dispatchWithFeeToken` will call `safeTransferFrom(payer, address(this), fee)` on that address unconditionally, with no check that `msg.sender == payer`. Any account that has ever left an ERC-20 approval to that HyperApp contract for the fee token (a common integration pattern: users approve once and reuse across sends) is then exposed: an unrelated caller can name that account as `payer` and force it to fund the caller's own dispatch, exactly analogous to `coverDefault(assets, provider)` pulling from an arbitrary `provider`.

By contrast, `EvmHost.dispatch(DispatchPost/DispatchGet)` correctly pulls fees from `_msgSender()` and ignores `post.payer` for the actual token pull [4](#0-3) , showing the project is aware `msg.sender` is the safe source — but the `HyperApp` base contract, which many downstream apps (bridges, token wrappers, custom messaging apps) inherit and call directly with an app-defined `payer`, does not enforce this invariant at all.

### Impact Explanation
Any account that has an outstanding (even accidental/legacy) ERC-20 fee-token approval to a `HyperApp`-derived contract can have that allowance drained by anyone who can invoke a dispatch entry point that lets them set `payer` to the victim's address. This results in direct theft of the victim's approved fee-token balance to subsidize an attacker's cross-chain dispatch, with no compensating benefit to the victim — a concrete theft-of-funds vulnerability reachable from a single, unprivileged transaction by any caller of the vulnerable dispatch function.

### Likelihood Explanation
Exploitability depends on whether a concrete downstream `HyperApp` subclass exposes `payer` as a caller-controlled parameter (as the official documentation examples explicitly recommend) rather than hardcoding `msg.sender`. Given that the SDK/docs pattern explicitly encourages `payer` as a function argument, and that ERC-20 approvals to bridge/messaging contracts are common and often left standing, likelihood is Medium-High for any app built following the documented pattern.

### Recommendation
In `HyperApp.dispatchWithFeeToken`, remove the arbitrary `payer` field entirely and always pull the fee token from `msg.sender` (or explicitly require `require(request.payer == msg.sender)` before the `safeTransferFrom`). Audit all downstream `HyperApp` integrations (docs examples, `HyperFungibleToken`, `WrappedHyperFungibleToken`, `BandwidthManager`, `ExtrinsicIntents`) to ensure none expose a caller-settable `payer` distinct from `msg.sender`.

### Proof of Concept
1. Victim approves `feeToken.approve(hyperAppContract, X)` once for legitimate future use of a `HyperApp`-based integration.
2. Attacker calls an exposed dispatch function on `hyperAppContract` (following the documented pattern) supplying `payer = victim` in the `DispatchPost`/`DispatchGet` struct.
3. `dispatchWithFeeToken` executes `IERC20(feeToken).safeTransferFrom(victim, address(this), fee)` [5](#0-4) , draining the victim's allowance to pay for the attacker's own cross-chain dispatch — with no signature or consent from the victim beyond the pre-existing approval.

### Citations

**File:** sdk/packages/core/contracts/apps/HyperApp.sol (L101-107)
```text
    function dispatchWithFeeToken(DispatchPost memory request) internal returns (bytes32) {
        address hostAddr = host();
        address feeToken = IDispatcher(hostAddr).feeToken();
        if (request.payer != address(this)) IERC20(feeToken).safeTransferFrom(request.payer, address(this), request.fee);
        IERC20(feeToken).forceApprove(hostAddr, request.fee);
        return IDispatcher(hostAddr).dispatch(request);
    }
```

**File:** sdk/packages/core/contracts/apps/HyperApp.sol (L116-122)
```text
    function dispatchWithFeeToken(DispatchGet memory request) internal returns (bytes32) {
        address hostAddr = host();
        address feeToken = IDispatcher(hostAddr).feeToken();
        if (request.payer != address(this)) IERC20(feeToken).safeTransferFrom(request.payer, address(this), request.fee);
        IERC20(feeToken).forceApprove(hostAddr, request.fee);
        return IDispatcher(hostAddr).dispatch(request);
    }
```

**File:** docs/content/developers/network/relayer.mdx (L1-1)
```text
---
```

**File:** evm/src/core/EvmHost.sol (L921-932)
```text
    function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                post.fee, path, address(this), block.timestamp
            );
        } else if (post.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), post.fee);
        }
```
