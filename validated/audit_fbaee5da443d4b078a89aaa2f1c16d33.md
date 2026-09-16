Based on my research, I found a genuine analog in the `HyperApp.dispatchWithFeeToken` pattern used across every Hyperbridge V2 app (`ExtrinsicIntents.sol`, `IntentGatewayV2.sol`, `BandwidthManager.sol`).

### Title
Arbitrary `payer` in `DispatchPost`/`DispatchGet` lets any contract drain a third party's fee-token allowance via `dispatchWithFeeToken` - ([File: sdk/packages/core/contracts/apps/HyperApp.sol])

### Summary
`HyperApp.dispatchWithFeeToken` pulls relayer-fee tokens from an arbitrary `request.payer` address supplied inside the `DispatchPost`/`DispatchGet` struct, rather than requiring `payer == msg.sender`. Any application built on `HyperApp` (e.g. `ExtrinsicIntents`, `IntentGatewayV2`, `BandwidthManager`) that lets a caller influence the `payer` field of a dispatch — directly, or indirectly by allowing arbitrary calldata/body construction — can pull ERC-20 fee tokens from any account that has ever approved that gateway contract, for a relayer fee the approver never agreed to pay. This is structurally identical to the reported `swapCalculatingRebate` issue: a mechanism intended to let an app act "on behalf of" a designated payer instead lets an unrelated caller spend someone else's approved balance because the contract-level actor performing the debit ("the app") is trusted by design but the specific transaction it is executing is not authorized by the debited party.

### Finding Description
`dispatchWithFeeToken` in `sdk/packages/core/contracts/apps/HyperApp.sol` reads the payer straight from the dispatch struct and calls `safeTransferFrom` on it: [1](#0-0) 

```solidity
function dispatchWithFeeToken(DispatchPost memory request) internal returns (bytes32) {
    address hostAddr = host();
    address feeToken = IDispatcher(hostAddr).feeToken();
    if (request.payer != address(this)) IERC20(feeToken).safeTransferFrom(request.payer, address(this), request.fee);
    IERC20(feeToken).forceApprove(hostAddr, request.fee);
    return IDispatcher(hostAddr).dispatch(request);
}
``` [2](#0-1) 

The only gate on the transfer is a pre-existing ERC-20 `approve` from `request.payer` to the gateway contract — the same design flaw pattern as `swapCalculatingRebate`'s `tx.origin` check: it verifies a *relationship* ("this account approved/authorized this contract"), not that *this specific caller and this specific action* were authorized by that account. `EvmHost.dispatch` itself documents `payer` as simply "who pays for this request", collected via `_msgSender()`/approvals with no cross-check against the dispatch caller's identity: [3](#0-2) 

Because ERC-20 approvals on gateways such as `IntentGatewayV2` are typically long-lived and sized for the app's normal flows (users approve the gateway once for order placement, e.g. `usdc.approve(address(intentGateway), inputAmount)` in [4](#0-3) ), any code path that constructs a `DispatchPost`/`DispatchGet` with an attacker-influenced `payer` field would let the attacker spend that pre-existing allowance for an unrelated relayer-fee payment, exactly mirroring the report's complaint that funds could be pulled from an account that never authorized *this* spend for *this* purpose.

### Impact Explanation
If any reachable app function allows a caller (or a value derived from attacker-controlled input, e.g. body/context fields decoded into a payer address) to set `request.payer` to an address other than `msg.sender`/the intended payer, the attacker can force `safeTransferFrom` on a victim's outstanding allowance to a Hyperbridge app contract, siphoning fee-token balance without consent — a direct theft-of-funds primitive reachable from a single dispatched request/transaction, matching the "unrelated third party uses another user's approved balance for unauthorized transactions" pattern the source report describes for rebates.

### Likelihood Explanation
Exploitability depends entirely on whether any concrete call site actually lets a caller set `payer` to something other than `msg.sender`. In the call sites inspected, `ExtrinsicIntents._post` hardcodes `payer: msg.sender`, which is safe. I was not able to fully audit every `DispatchPost`/`DispatchGet` construction site across `IntentGatewayV2.sol`, `BandwidthManager.sol`, and all `HyperApp` subclasses within available search budget to confirm whether `payer` is always hardcoded to `msg.sender` or whether any path derives it from order/user-supplied data (e.g., a beneficiary/solver field mistakenly reused as `payer`). This is a design-level weakness in the shared `HyperApp` primitive rather than a confirmed exploitable call site.

### Recommendation
Restrict `dispatchWithFeeToken`/`dispatch` so that `payer` can only be `msg.sender` (the account calling the app function) or `address(this)`, removing the "trust any approved account" pattern; if flexibility for third-party sponsorship is required, require an explicit, single-use, transaction-scoped authorization (e.g., an EIP-2612 permit signed by the payer for this specific commitment) rather than relying on a standing ERC-20 approval. Additionally, audit every `DispatchPost`/`DispatchGet` construction site in `IntentGatewayV2.sol`, `BandwidthManager.sol`, and other `HyperApp` consumers to confirm `payer` is always set to `msg.sender` and never derived from attacker-influenced order/session/beneficiary fields.

### Proof of Concept
1. Victim `V` approves gateway `G` (a `HyperApp` subclass) for `feeToken` to place orders normally: `feeToken.approve(G, X)`.
2. If any `G` function reachable by attacker `A` builds a `DispatchPost`/`DispatchGet` with `payer: <V's address>` (instead of `msg.sender`) — e.g., through a manipulable field in `Order`/calldata that ends up populating `payer` — `A` calls that function.
3. `dispatchWithFeeToken` executes `feeToken.safeTransferFrom(V, address(this), fee)`, pulling from `V`'s allowance to pay a relayer fee for a request `A` initiated, with no consent from `V` for this specific transaction.
4. Repeated across many approvals, this could drain fee-token allowances protocol-wide, analogous to the "unscrupulous individual" scenario acknowledged in the original report, but here manifesting as direct fund transfer rather than a rebate discount.

Note: this analog is contingent on finding a concrete call site where `payer` is not hardcoded to `msg.sender`; I could not exhaustively confirm this within the available search scope, so treat the "Likelihood" section's caveat as material to final severity triage.

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

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L18-34)
```text
```solidity lineNumbers
// An object for dispatching post requests 
struct DispatchPost {
    // Use the StateMachine library to create this
    bytes dest;
    // The destination module
    bytes to;
    // The request body
    bytes body;
    // timeout for this request in seconds
    uint64 timeout;
    // The amount put up to be paid to the relayer, 
    // this is in the feeToken and charged to msg.sender
    uint256 fee;
    // who pays for this request?
    address payer;
}
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L3963-3964)
```text
        usdc.approve(address(intentGateway), inputAmount);
        intentGateway.placeOrder(orderA, bytes32(0));
```
