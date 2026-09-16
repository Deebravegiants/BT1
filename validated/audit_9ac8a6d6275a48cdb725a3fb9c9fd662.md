### Title
Permanent loss of ETH accidentally sent to `HostManager` with no recovery mechanism - (File: `evm/src/core/HostManager.sol`)

### Summary
`HostManager` implements a bare `receive() external payable {}` fallback with a comment warning "Do not send any tokens directly to this contract," but the contract provides no function to recover native ETH that lands in its own balance. This mirrors the reported `OptimismPortal.donateETH()` issue: a payable entry point exists for a specific migration/operational purpose, but nothing lets governance or anyone else move out ETH that ends up stuck there, so any ETH sent directly to `HostManager` is permanently frozen.

### Finding Description
`HostManager` declares: [1](#0-0) 

The only other place the contract touches value is `onAccept`, which handles governance actions (`Withdraw`, `SetHostParam`, `SetAdmin`) delivered from Hyperbridge via ISMP: [2](#0-1) 

Crucially, the `Withdraw` action calls `IHostManager(_params.host).withdraw(withdrawParams)` — i.e. it withdraws revenue held by the `EvmHost` contract, not funds held by `HostManager` itself: [3](#0-2) 

`EvmHost.withdraw()` only moves `address(this).balance` (the host's own balance), and is restricted to being called by `_hostParams.hostManager`: [4](#0-3) 

So there is no code path — governance or otherwise — that moves ETH out of `HostManager`'s own balance. Any ETH sent to the `HostManager` address (accidentally, via a wrong integration, a misrouted refund from another contract, or a user mistake) is permanently stuck, exactly like the excess-ether-to-`donateETH` scenario in the reported OptimismPortal issue. Other contracts in the codebase that accept a bare `receive()` for a similar "collect dust" purpose (e.g. `EvmHost`, `IntentGatewayV2`) do have a corresponding sweep/withdraw mechanism (`EvmHost.withdraw()`, `IntentsBase._sweepDust()` reachable via `RequestKind.SweepDust`), but `HostManager` has none.

### Impact Explanation
Any native ETH transferred to the `HostManager` contract is permanently frozen with no possible recovery — not by governance, not by the admin, not by any privileged or unprivileged actor. This is a permanent loss-of-funds bug class (Medium per the reference report), reachable by a single unprivileged transaction (a plain ETH transfer) to a contract address that is a standard, documented part of the deployed Hyperbridge EVM host stack.

### Likelihood Explanation
`HostManager` is a core, publicly known contract address in each EVM deployment (paired 1:1 with `EvmHost`). Its own comment acknowledges that ETH might be sent there ("Do not send any tokens directly to this contract"), which signals the developers anticipated but did not guard against or provide a remedy for this scenario. Accidental transfers (e.g., wrong contract address, a refund path, or a misconfigured integration sending value alongside a call) are a realistic occurrence given how many hyperbridge peripheral contracts accept and forward native value.

### Recommendation
Add a privileged (governance/admin-gated) sweep function to `HostManager` that transfers its own native ETH balance (and optionally any ERC-20 dust) to a specified beneficiary, analogous to `EvmHost.withdraw()` or `IntentsBase._sweepDust()`/`RequestKind.SweepDust`, so ETH accidentally sent to `HostManager` is not permanently lost.

### Proof of Concept
1. Any account sends ETH directly to the deployed `HostManager` contract address (e.g., `(bool ok,) = hostManagerAddr.call{value: 1 ether}("")`), which succeeds because of `receive() external payable {}`.
2. Balance now sits in `HostManager`.
3. Inspect all callable functions on `HostManager`: `params()`, `host()`, `relayer()`, `init()`, `onAccept()`. None of them transfer `HostManager`'s own native balance to any address — `onAccept`'s `Withdraw` branch only calls `EvmHost.withdraw()`, which operates on `EvmHost`'s own balance, restricted to `_hostParams.hostManager` as caller, and has no way to pull funds sitting in `HostManager`.
4. The ETH sent in step 1 is unrecoverable by any account, including governance/admin, for the lifetime of the contract.

### Citations

**File:** evm/src/core/HostManager.sol (L83-86)
```text
    /*
     * @dev fallback function for tests. Do not send any tokens directly to this contract.
     */
    receive() external payable {}
```

**File:** evm/src/core/HostManager.sol (L134-159)
```text
    function onAccept(IncomingPostRequest calldata incoming)
        external
        override
        restrict(msg.sender, _params.host)
        restrict(incoming.relayer, _params.admin)
    {
        PostRequest calldata request = incoming.request;
        // Only the Hyperbridge parachain can send requests to this module.
        if (!request.source.equals(IHost(_params.host).hyperbridge())) revert UnauthorizedAction();

        OnAcceptActions action = OnAcceptActions(uint8(request.body[0]));
        if (action == OnAcceptActions.Withdraw) {
            // This is where governance & relayers can withdraw their revenue.
            WithdrawParams memory withdrawParams = abi.decode(request.body[1:], (WithdrawParams));
            IHostManager(_params.host).withdraw(withdrawParams);
        } else if (action == OnAcceptActions.SetHostParam) {
            HostParams memory hostParams = abi.decode(request.body[1:], (HostParams));
            IHostManager(_params.host).updateHostParams(hostParams);
        } else if (action == OnAcceptActions.SetAdmin) {
            // Rotates the governance relayer.
            address newAdmin = abi.decode(request.body[1:], (address));
            if (newAdmin == address(0)) revert InvalidAdmin();
            emit AdminUpdated({previous: _params.admin, current: newAdmin});
            _params.admin = newAdmin;
        }
    }
```

**File:** evm/src/core/EvmHost.sol (L647-660)
```text
    /**
     * @dev withdraws host revenue to the given address, can only be called by cross-chain governance
     * @param params, the parameters for withdrawal
     */
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
