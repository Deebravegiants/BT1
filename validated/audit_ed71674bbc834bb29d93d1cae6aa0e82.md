### Title
Attacker can permanently grief the EvmHost fee-token migration via a 1-wei direct token transfer - (`evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.updateHostParamsInternal` refuses to change `feeToken` unless the host's balance of the *old* fee token is exactly zero. Because any external account can transfer a trivial amount of that ERC20 directly to the host contract at will, an attacker can keep this balance non-zero indefinitely, permanently blocking cross-chain governance from ever migrating the fee token — the same griefing pattern as the referenced `RioLRTAssetRegistry.removeAsset()` report, where a balance-must-be-zero precondition is trivially defeated by an unprivileged direct transfer.

### Finding Description
`updateHostParamsInternal` gates any change of `feeToken` on the host's current balance of the outgoing token being zero: [1](#0-0) 

```solidity
address oldFeeToken = feeToken();
if (oldFeeToken != address(0) && oldFeeToken != params.feeToken) {
    uint256 balance = IERC20(oldFeeToken).balanceOf(address(this));
    if (balance != 0) revert CannotChangeFeeToken();
}
```

This is only reachable through cross-chain governance: `HostManager.onAccept` decodes a `SetHostParam` action and calls `IHostManager(_params.host).updateHostParams(hostParams)` [2](#0-1) , which in turn is `restrict(_hostParams.hostManager)`-gated on the host side [3](#0-2) .

Since the fee token is an ordinary ERC20 (e.g. DAI), **any address holding it can call `transfer(host, 1)`** at any time — no permission is required to move tokens *into* the host, only the governance-gated `withdraw()` can move them *out* [4](#0-3) . Because ISMP governance actions (`withdraw` and `updateHostParams`) are delivered as separate, asynchronous cross-chain requests via the `HostManager` relayer path rather than atomically in one transaction, an attacker can always re-fund the balance with a 1-wei transfer between the moment governance's `withdraw` sweep lands and the moment the subsequent `SetHostParam` request is delivered, reproducing the exact griefing window described in the referenced report.

The unit test `testSweepFeeTokenBeforeUpdate` in `EvmHostTest.sol` confirms the precondition and shows that even a full sweep (`feeToken.burn`) is required before the update can proceed — there is no code path that lets governance force the fee-token migration while a residual balance remains [5](#0-4) .

### Impact Explanation
An unprivileged attacker holding a negligible amount of the current fee token can indefinitely prevent Hyperbridge governance from rotating away from a compromised, deprecated, or otherwise problematic fee token on any `EvmHost` deployment. This is a permanent denial-of-service on a protocol-critical governance action (fee-token migration), matching the Medium-severity "asset removal griefing" class in the reference report — it does not itself steal funds, but it permanently freezes governance's ability to perform an intended, security-relevant configuration change.

### Likelihood Explanation
Trivial to execute: sending 1 wei of an ERC20 to a known contract address requires no special permission, gas cost is negligible, and it can be repeated indefinitely (each time governance clears the balance) to keep blocking the update. The only cost to the attacker is the price of the smallest transferable unit of the fee token and gas.

### Recommendation
Remove the "balance must be zero" precondition for changing `feeToken`, or replace it with a governance-controlled sweep executed atomically as part of the same `updateHostParams` call (e.g., automatically transferring any residual old-fee-token balance to a specified beneficiary within `updateHostParamsInternal` itself, rather than requiring a separate prior `withdraw` call that can be re-griefed before the update lands).

### Proof of Concept
1. Host is configured with `feeToken = DAI`, and governance wants to migrate to `feeToken = USDC`.
2. Attacker holds ≥1 wei of DAI (any amount, even dust) and calls `DAI.transfer(address(EvmHost), 1)` — no access control prevents this since the host's fallback/`receive` and ERC20 transfers accept from anyone.
3. Governance's cross-chain `SetHostParam` request (with `params.feeToken = USDC`) arrives via `HostManager.onAccept` → `EvmHost.updateHostParams` → `updateHostParamsInternal`.
4. `IERC20(DAI).balanceOf(address(this)) != 0` (attacker's 1 wei), so the call reverts with `CannotChangeFeeToken` (`evm/src/core/EvmHost.sol:617-621`), and the delivered request is dropped/undelivered.
5. Even if governance first dispatches a `withdraw` action to sweep the DAI balance to zero, the attacker can re-send 1 wei of DAI to the host in the window between the `withdraw` request being delivered and the subsequent `SetHostParam` request being delivered (these are two independent, asynchronously-relayed cross-chain messages, not one atomic transaction), repeating step 4 indefinitely.

### Citations

**File:** evm/src/core/EvmHost.sol (L573-575)
```text
    function updateHostParams(HostParams memory params) external virtual restrict(_hostParams.hostManager) {
        updateHostParamsInternal(params);
    }
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

**File:** evm/src/core/HostManager.sol (L149-151)
```text
        } else if (action == OnAcceptActions.SetHostParam) {
            HostParams memory hostParams = abi.decode(request.body[1:], (HostParams));
            IHostManager(_params.host).updateHostParams(hostParams);
```

**File:** evm/tests/foundry/EvmHostTest.sol (L102-116)
```text
    function testSweepFeeTokenBeforeUpdate() public {
        feeToken.mint(address(host), 1 * 1e18);
        HostParams memory params = host.hostParams();
        params.feeToken = address(this);
        // we can't set host params
        vm.prank(host.hostParams().admin);
        vm.expectRevert(EvmHost.CannotChangeFeeToken.selector);
        host.updateHostParams(params);

        feeToken.burn(address(host), 1 * 1e18);
        // we can set host params
        vm.prank(host.hostParams().admin);
        host.updateHostParams(params);
        assert(host.hostParams().feeToken == address(this));
    }
```
