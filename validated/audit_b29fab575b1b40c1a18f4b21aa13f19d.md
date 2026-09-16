I have enough evidence to write the analog finding now.

### Title
Governance-triggered fee-token migration in `EvmHost.updateHostParamsInternal` can be permanently blocked by dust-transferring the old fee token to the host - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.updateHostParamsInternal` refuses to switch the protocol's `feeToken` while the host contract's balance of the *old* fee token is non-zero, exactly mirroring the `PirexGmx.initiateMigration` pattern where `RewardRouterV2.signalTransfer` refuses to proceed while the caller holds vester tokens. In both cases, an unprivileged party can force the guarded balance to be non-zero by simply transferring a standard, freely-transferable ERC-20 token to the target contract, permanently blocking a privileged/governance state transition.

### Finding Description
`updateHostParamsInternal` contains this invariant check before applying new `HostParams`: [1](#0-0) 

```solidity
address oldFeeToken = feeToken();
if (oldFeeToken != address(0) && oldFeeToken != params.feeToken) {
    uint256 balance = IERC20(oldFeeToken).balanceOf(address(this));
    if (balance != 0) revert CannotChangeFeeToken();
}
```

Unlike `gmxVester`/`glpVester` (which are non-transferrable, per the PirexGmx report's rebuttal), the ISMP protocol's `feeToken` is an ordinary ERC-20 (e.g. USDC/DAI/WETH) used to pay dispatch fees throughout the protocol — `EvmHost.withdraw`, `BandwidthManager`, `HostManager.onAccept`'s `Withdraw` action, and every fee-paying dispatch route it. Since ERC-20 `transfer` is unrestricted, **any address** can call `IERC20(oldFeeToken).transfer(evmHostAddress, 1)` at any time, from any account, with no special privilege. This sets `balanceOf(address(this)) != 0` and causes every subsequent `updateHostParams` call attempting to change `feeToken` to revert with `CannotChangeFeeToken`, regardless of the `restrict(_hostParams.hostManager)` modifier gating who can invoke it: [2](#0-1) 

`updateHostParams` is reachable only through Hyperbridge's cross-chain governance path — `HostManager.onAccept` decodes a `SetHostParam` action dispatched from the Hyperbridge parachain and calls `IHostManager(_params.host).updateHostParams(hostParams)`: [3](#0-2) 

There is no sweep/rescue function visible in `EvmHost` that lets governance drain an arbitrary residual balance of the *old* fee token before retrying the update — `withdraw` pays out host revenue to a beneficiary chosen by governance but is itself gated behind the same `hostManager` restrict path and does not target "drain old fee token to zero" as a distinct, always-available operation independent of the stuck migration. Because the check compares the *entire* contract balance rather than a protocol-tracked accrued-fee balance, a griefer's 1-wei donation is indistinguishable on-chain from legitimate unclaimed host revenue, so any attempted mitigation that just force-sweeps the balance also risks socializing/dropping real relayer/protocol fee accounting.

### Impact Explanation
This blocks a core governance capability: rotating the protocol's fee token (e.g. in response to a compromised/deprecated token, a required migration to a new stablecoin, or a Uniswap routing change referenced in the `HostParams.feeToken` docs). Since the block is indefinite and trivially re-triggerable (the attacker can keep re-donating 1 wei every time governance tries to sweep and retry), this is a **permanent freezing of a critical, unprivileged-reachable dispatch parameter**, matching the "route unable to deliver messages"/"unauthorized app action blocked" class Hyperbridge treats as Medium/High. Because `feeToken` gates how every dispatcher on the chain pays for cross-chain messages, being unable to migrate it under adversarial conditions (e.g., the old fee token is compromised, depegged, or blacklisting the host) can leave the entire EVM host stuck paying fees in a token operators no longer want.

### Likelihood Explanation
Trivial and cheap to execute: it only requires one ERC-20 `transfer` call of the smallest possible unit of the current `feeToken` to the known, public `EvmHost` address. It requires no special timing, no governance compromise, and can be repeated by any address indefinitely, so it will reliably block any legitimate `SetHostParam` fee-token rotation attempt as long as the attacker is watching for it (which is cheap to automate).

### Recommendation
Do not gate the fee-token change on the *contract's total balance* of the old token. Instead:
- Track accrued/unclaimed host revenue in the old fee token in a dedicated state variable (separate from raw `balanceOf`), and require that internal counter to be zero (or auto-sweep it to the configured beneficiary) rather than checking `IERC20.balanceOf(address(this))`.
- Alternatively, remove the zero-balance precondition entirely and instead auto-transfer any residual old-fee-token balance to the outgoing beneficiary/treasury as part of `updateHostParamsInternal` itself, so the update always succeeds and any dust (griefer-donated or legitimate) is swept atomically rather than used as a block vector.

### Proof of Concept
1. Governance (via Hyperbridge) prepares a `SetHostParam` action to rotate `EvmHost.feeToken` from `USDC` to `DAI`.
2. Before the message lands, an attacker (or anyone) calls `USDC.transfer(evmHostAddress, 1)`.
3. `HostManager.onAccept` delivers the `SetHostParam` request, calling `EvmHost.updateHostParams(newParams)` → `updateHostParamsInternal`.
4. `feeToken()` returns the old `USDC` address; `IERC20(USDC).balanceOf(address(this))` is now `1` (attacker-donated) → `revert CannotChangeFeeToken()`.
5. The governance-dispatched fee-token rotation request fails and, per the ISMP request-handling semantics, is either dropped or must be retried — the attacker repeats step 2 on every retry, permanently blocking the rotation.

### Citations

**File:** evm/src/core/EvmHost.sol (L564-576)
```text
    /**
     * @dev Updates the HostParams. Only callable by cross-chain governance
     * via the configured `hostManager`. The admin has no privileges here —
     * environments that need a privileged admin override (testnets, forks)
     * should use `TestnetHost`, which extends this contract.
     *
     * Marked `virtual` so subclasses can broaden the authorization
     * @param params, the new host params.
     */
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

**File:** evm/src/core/HostManager.sol (L149-151)
```text
        } else if (action == OnAcceptActions.SetHostParam) {
            HostParams memory hostParams = abi.decode(request.body[1:], (HostParams));
            IHostManager(_params.host).updateHostParams(hostParams);
```
