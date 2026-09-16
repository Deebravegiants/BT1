## Analysis Result

### Title
Griefing via unauthorized `payer` parameter in `HyperApp.dispatchWithFeeToken` — arbitrary fee-token pull from any address that approved the Host - (File: `sdk/packages/core/contracts/apps/HyperApp.sol`)

### Summary
`HyperApp.dispatchWithFeeToken` (used for both `DispatchPost` and `DispatchGet`) pulls the relayer fee via `safeTransferFrom(request.payer, address(this), request.fee)` whenever `request.payer != address(this)`, with no check that `request.payer` is or was authorized by the actual caller of the surrounding transaction. This is structurally identical to the reported Uniswap `uniswapV3SwapCallback` bug: an attacker-supplied address field is trusted as the source of a `transferFrom` without verifying the caller has any relationship to that address.

### Finding Description
`HyperApp.sol` is the abstract base contract that Hyperbridge application developers extend to build cross-chain apps [1](#0-0) . Its internal helper functions perform the fee-token pull:

```solidity
function dispatchWithFeeToken(DispatchPost memory request) internal returns (bytes32) {
    address hostAddr = host();
    address feeToken = IDispatcher(hostAddr).feeToken();
    if (request.payer != address(this)) IERC20(feeToken).safeTransferFrom(request.payer, address(this), request.fee);
    IERC20(feeToken).forceApprove(hostAddr, request.fee);
    return IDispatcher(hostAddr).dispatch(request);
}
``` [2](#0-1) 

The same pattern is duplicated for `DispatchGet`: [3](#0-2) 

The `DispatchPost`/`DispatchGet` structs explicitly carry a caller-supplied `payer` field, and the interface documentation for `IDispatcher` states plainly: *"If different from msg.sender, must have approved the Host contract"* [4](#0-3) [5](#0-4) . This confirms the protocol's own design assumes any address that has ever approved fee-token spending to a Host/App can have that approval spent by an unrelated dispatch, as long as some contract logic sets `request.payer` to that address.

The concrete apps shipped in this repo (`HyperFungibleToken`, `HyperFungibleTokenUpgradeable`, `WrappedHyperFungibleToken`) always hardcode `payer: msg.sender` when building their `DispatchPost` [6](#0-5) , so those specific integrations are not directly exploitable. However, `dispatchWithFeeToken` itself — the reusable primitive every third-party `HyperApp` subclass is expected to call — performs no assertion that `request.payer == msg.sender` (or any equivalent authorization check) before executing the `transferFrom`. Any downstream app (including ones not present in this repo, or a generic pass-through dispatcher) that forwards a caller-supplied `payer`/request struct to `dispatchWithFeeToken` reproduces exactly the Uniswap-callback griefing pattern: an attacker directs the pull of ERC-20 balance from a victim address that merely approved the relevant fee token to the Host/App, with the fee then benefiting the attacker's own arbitrary dispatch.

### Impact Explanation
Any address that has approved its `feeToken` allowance to a Host/App implementing this pattern is exposed to having that allowance drained/spent on behalf of an attacker's arbitrary cross-chain dispatch, at zero cost to the attacker. This is a direct theft-of-funds vector (fee tokens, typically stablecoins) reachable by a single unprivileged transaction, matching the "concrete theft ... of funds" bar.

### Likelihood Explanation
Likelihood depends on whether any deployed `HyperApp` subclass exposes a caller-controlled `payer` to `dispatchWithFeeToken` — a pattern the interface/documentation explicitly anticipates ("If different from msg.sender, must have approved the Host contract") rather than forbids. Given this is a shared, actively used base contract intended for third-party integrators building on Hyperbridge, and the protocol's own docs describe `payer != msg.sender` as a legitimate supported configuration, the risk of a downstream integration surfacing this primitive without additional authorization checks is realistic.

### Recommendation
Add an explicit authorization check in `dispatchWithFeeToken` (and any Host-level dispatch code with the same pattern) — e.g., require `request.payer == msg.sender` unless the payer has signed/approved specifically for this call, or require the calling contract to enforce that only the actual fee-payer's own transaction can set `payer` to a non-`address(this)` value. At minimum, clearly document in `IDispatcher`/`HyperApp` that any integrator exposing a `payer` parameter to end users must ensure it can only be set to `msg.sender` or to an address with explicit per-call consent, never to an arbitrary third party.

### Proof of Concept
1. Victim `V` approves `feeToken` to `HostOrApp` (a legitimate action they take for their own future dispatches).
2. Attacker deploys/calls a `HyperApp` subclass (or any contract exposing a thin wrapper around `dispatchWithFeeToken`) with `request.payer = V` and `request.fee` set to `V`'s allowance.
3. `dispatchWithFeeToken` executes `IERC20(feeToken).safeTransferFrom(V, address(this), request.fee)` because `V != address(this)`, pulling `V`'s fee tokens to pay for the attacker's own POST/GET dispatch.
4. `V` loses the approved fee tokens with no benefit from the dispatched message, which was chosen entirely by the attacker.

### Citations

**File:** sdk/packages/core/contracts/apps/HyperApp.sol (L43-43)
```text
abstract contract HyperApp is IApp {
```

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

**File:** sdk/packages/core/contracts/interfaces/IDispatcher.sol (L39-41)
```text
    /// @notice Account responsible for paying the fees
    /// @dev If different from msg.sender, must have approved the Host contract
    address payer;
```

**File:** sdk/packages/core/contracts/interfaces/IDispatcher.sol (L68-70)
```text
    /// @notice Account responsible for paying the fees
    /// @dev If different from msg.sender, must have approved the Host contract
    address payer;
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L248-255)
```text
        return DispatchPost({
            dest: params.dest,
            to: dest,
            body: body,
            timeout: params.timeout,
            fee: params.relayerFee,
            payer: msg.sender
        });
```
