### Title
Fee-token migration in `EvmHost.updateHostParamsInternal` can be permanently blocked by dust-transfer front-running - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.updateHostParamsInternal` refuses to change the configured `feeToken` while the host contract holds *any* non-zero balance of the old fee token. Because any unprivileged holder of that ERC-20 can transfer a trivial (even 1-wei) amount to the host contract at will, an attacker can keep the balance permanently non-zero and thereby block every legitimate governance attempt to migrate the fee token, indefinitely.

### Finding Description
`updateHostParamsInternal` performs the following check before applying a new `HostParams`: [1](#0-0) 

```solidity
address oldFeeToken = feeToken();
if (oldFeeToken != address(0) && oldFeeToken != params.feeToken) {
    uint256 balance = IERC20(oldFeeToken).balanceOf(address(this));
    if (balance != 0) revert CannotChangeFeeToken();
}
```

This function is invoked either directly through the externally-callable, `hostManager`-restricted `updateHostParams` [2](#0-1)  or indirectly through cross-chain governance dispatched via `HostManager.onAccept`, as exercised in the test harness [3](#0-2) .

The `feeToken` is a normal ERC-20 contract (e.g. a stablecoin) that every dispatcher, app, relayer, and bandwidth purchaser interacts with by design — anyone can hold it and transfer it to arbitrary addresses, including the host contract itself, with no permission required (see how the fee token is universally read/used by dApps: `IDispatcher(_host).feeToken()` in `HyperApp.sol` [4](#0-3) , and in the bandwidth purchase flow [5](#0-4) ).

Because the check is a strict `balance != 0` revert rather than an automatic sweep/withdrawal of the stranded balance, any unprivileged actor holding even a trivial amount of the current fee token can:
1. Detect (or front-run, on chains where possible) a pending `updateHostParams` call that changes `feeToken`.
2. Transfer 1 wei (or any amount) of the old fee token to the `EvmHost` contract address.
3. Cause the entire governance-initiated `updateHostParamsInternal` call to revert with `CannotChangeFeeToken`.

This is structurally identical to the reported `YRizStrategy._checkPoolsWithBalanceAreIncluded` bug class: a state-mutating administrative operation is gated by a "balance must be zero" invariant with no automated remediation path, letting any unprivileged party keep that invariant permanently false and thereby veto the operation forever.

### Impact Explanation
If Hyperbridge governance ever needs to migrate away from the currently configured fee token (e.g. the token becomes compromised, gets its liquidity drained, is deprecated, has a bug, or the issuer blacklists the host contract), an attacker can permanently prevent that migration by keeping a non-zero balance of the old token in the host contract. Since fee-token payment underlies dispatch of every POST/GET request through `dispatchWithFeeToken` [4](#0-3) , an inability to migrate a broken/compromised fee token can degrade or halt the ability of apps to dispatch new cross-chain messages on that host — i.e., a route becoming unable to deliver messages, since dispatch fee payment is stuck referencing a fee token that no longer functions.

### Likelihood Explanation
The attack requires no privilege and costs at most a few wei of the fee token plus gas for an ordinary ERC-20 `transfer`. It can be repeated indefinitely and does not require front-running specifically — a monitoring bot watching for `updateHostParams`/governance dispatch transactions in the mempool, or simply periodically re-topping-up the balance, is sufficient to keep it permanently blocked. This makes the likelihood high once an attacker has motive (e.g., to force continued use of a token they can manipulate, or simply to grief the protocol).

### Recommendation
Do not revert the entire host-params update when the old fee token still holds a balance. Instead, either:
- Automatically sweep/withdraw the residual old-fee-token balance to a safe destination (e.g. `_hostParams.admin`/treasury) as part of `updateHostParamsInternal`, or
- Decouple the balance-sweep from the params update entirely (allow the fee token to be swapped immediately, and let governance later reclaim residual old-token balance via the existing `withdraw` function), removing the hard dependency between "balance is zero" and "fee token can be changed."

### Proof of Concept
1. Governance prepares a `HostParams` update that changes `feeToken` from `TokenA` to `TokenB`, to be delivered via `updateHostParams`/`HostManager.onAccept`.
2. Any address holding `TokenA` calls `TokenA.transfer(address(host), 1)` before the governance transaction lands (or simply keeps doing this periodically).
3. `updateHostParamsInternal` computes `IERC20(oldFeeToken).balanceOf(address(this))` as non-zero and reverts with `CannotChangeFeeToken` at [1](#0-0) , exactly the same class of self-inflicted DoS as `_checkPoolsWithBalanceAreIncluded` reverting on a pool with dust balance in the original report.
4. The attacker repeats step 2 whenever the balance is swept to zero, permanently blocking any future fee-token migration on that host.

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

**File:** evm/tests/foundry/HostManagerTest.sol (L320-328)
```text
    function HostManagerSetParams(PostRequest calldata request) public {
        vm.startPrank(address(host));

        HostManager(payable(host.hostParams().hostManager)).onAccept(IncomingPostRequest(request, tx.origin));
        HostParams memory params = abi.decode(request.body[1:], (HostParams));
        console.logUint(host.hostParams().challengePeriod);

        require(host.hostParams().challengePeriod == params.challengePeriod, "Failed to process request");
    }
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

**File:** docs/content/developers/evm/bandwidth/purchasing.mdx (L94-101)
```text
    /// Quote the fee-token cost of a `(tier, months)` purchase.
    function quote(uint256 tier, uint256 months) public view returns (uint256) {
        uint256 price18d = manager.tierPrice(tier);
        uint256 total18d = price18d * months;
        address feeToken = IDispatcher(host).feeToken();
        uint8 dec = IERC20Metadata(feeToken).decimals();
        return total18d / (10 ** (18 - dec));
    }
```
