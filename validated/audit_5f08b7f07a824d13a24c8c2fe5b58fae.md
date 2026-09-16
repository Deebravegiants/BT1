## Analog Found

### Title
Attacker can permanently block fee-token migration in `EvmHost` by donating 1 wei of the old fee token - (`File: evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.updateHostParamsInternal` refuses to change `hostParams.feeToken` whenever the current fee token still has a nonzero balance on the host contract. Because any address can transfer ERC-20 tokens to the host without permission, an attacker can perpetually "top up" the old fee token balance with a single wei to force this check to fail, permanently blocking governance's ability to migrate the protocol's fee token — the same bug class as the referenced Rio report, where a griefer donates 1 wei to block a balance-gated state transition.

### Finding Description
`updateHostParamsInternal` contains: [1](#0-0) 

```solidity
address oldFeeToken = feeToken();
if (oldFeeToken != address(0) && oldFeeToken != params.feeToken) {
    uint256 balance = IERC20(oldFeeToken).balanceOf(address(this));
    if (balance != 0) revert CannotChangeFeeToken();
}
```

This mirrors the reported pattern exactly: a balance-based precondition gates a privileged state transition, but the balance itself is influenced by an unprivileged party via a plain ERC-20 transfer (`IERC20(oldFeeToken).transfer(host, 1)`), which requires no allowance or permission from the recipient. The host contract has no mechanism to reject or refuse incoming ERC-20 transfers.

Migrating the fee token is a two-step governance flow: Hyperbridge dispatches a `Withdraw` action to drain the old fee-token balance to zero via `EvmHost.withdraw` [2](#0-1) , then a separate `SetHostParam` action calling `updateHostParams` with the new `feeToken`. These are delivered as two independent ISMP `PostRequest`s through `HostManager.onAccept` [3](#0-2) , each requiring its own relayed, provable delivery — meaning they cannot be bundled into a single atomic transaction. Because relayed governance deliveries are publicly observable on-chain before/at execution, an attacker can watch for the `withdraw` delivery and, in the same or a following block, send 1 wei of the old fee token to the host address, reinstating a nonzero balance before the `updateHostParams` delivery lands and causing `CannotChangeFeeToken()` to revert.

### Impact Explanation
This lets any unprivileged party indefinitely block a legitimate, privileged, cross-chain governance action (fee-token migration) on any `EvmHost` deployment. Fee-token migration is a documented protocol capability (`HostParams.feeToken` docstring: "we allow it to be configurable to prevent future regrets" [4](#0-3) ), used, e.g., if the current fee token becomes compromised, deprecated, or needs replacement. A griefer can hold this critical migration path hostage indefinitely for the cost of dust transfers, which is a governance-function freezing condition — matching the "route unable to deliver messages" / permanent freezing category.

### Likelihood Explanation
The attack requires no special access: any address can call `transfer`/`transferFrom` against the fee-token ERC-20 to send funds to the (publicly known) `EvmHost` address at any time, including immediately after observing a `Withdraw` governance delivery in the mempool or a subsequent block, since the two governance messages cannot be delivered atomically. The cost to the attacker is negligible (1 wei of the token plus gas), and the griefing can be repeated indefinitely each time governance attempts the migration.

### Recommendation
Do not gate `feeToken` migration on the token's on-chain balance at the host. Instead, either (a) sweep any residual balance of the outgoing fee token automatically as part of `updateHostParamsInternal` (e.g., transfer it to the configured beneficiary/hostManager) rather than reverting, or (b) drop the balance check entirely and let a subsequent `withdraw` call to the old token address recover any residual/dust balance after the swap, since `withdraw` already supports withdrawing by arbitrary `token` address regardless of the currently configured `feeToken`.

### Proof of Concept
1. Governance (via Hyperbridge) dispatches a `Withdraw` `PostRequest` to zero out the host's balance of the current `feeToken` (`OnAcceptActions.Withdraw` → `EvmHost.withdraw`).
2. An attacker observing this delivery (or simply monitoring the host's fee-token balance) calls `feeToken.transfer(hostAddress, 1)` right after the withdrawal executes, or even preemptively at any point before the next `updateHostParams` delivery.
3. Governance's subsequent `SetHostParam` `PostRequest` (encoding a `HostParams` with a different `feeToken`) is delivered to `HostManager.onAccept`, which calls `EvmHost.updateHostParams` → `updateHostParamsInternal`.
4. `IERC20(oldFeeToken).balanceOf(address(this))` returns `1` (nonzero), so the call reverts with `CannotChangeFeeToken()` [1](#0-0) , and per `EvmHost.dispatchIncoming`'s failure handling the delivery is recorded as refused/undelivered, requiring retry — which the attacker can repeat indefinitely with another 1-wei transfer.

### Citations

**File:** evm/src/core/EvmHost.sol (L42-44)
```text
    // The fee token contract address. This will typically be DAI.
    // but we allow it to be configurable to prevent future regrets.
    address feeToken;
```

**File:** evm/src/core/EvmHost.sol (L617-621)
```text
        address oldFeeToken = feeToken();
        if (oldFeeToken != address(0) && oldFeeToken != params.feeToken) {
            uint256 balance = IERC20(oldFeeToken).balanceOf(address(this));
            if (balance != 0) revert CannotChangeFeeToken();
        }
```

**File:** evm/src/core/EvmHost.sol (L651-660)
```text
    function withdraw(WithdrawParams memory params) external restrict(_hostParams.hostManager) {
        if (params.token == address(0)) {
            // this is safe because re-entrancy is mitigated before dispatching requests
            (bool sent,) = params.beneficiary.call{value: params.amount}("");
            if (!sent) revert WithdrawalFailed();
        } else {
            IERC20(params.token).safeTransfer(params.beneficiary, params.amount);
        }
        emit HostWithdrawal({beneficiary: params.beneficiary, amount: params.amount, token: params.token});
    }
```

**File:** evm/src/core/HostManager.sol (L144-151)
```text
        OnAcceptActions action = OnAcceptActions(uint8(request.body[0]));
        if (action == OnAcceptActions.Withdraw) {
            // This is where governance & relayers can withdraw their revenue.
            WithdrawParams memory withdrawParams = abi.decode(request.body[1:], (WithdrawParams));
            IHostManager(_params.host).withdraw(withdrawParams);
        } else if (action == OnAcceptActions.SetHostParam) {
            HostParams memory hostParams = abi.decode(request.body[1:], (HostParams));
            IHostManager(_params.host).updateHostParams(hostParams);
```
