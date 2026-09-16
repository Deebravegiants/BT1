### Title
`updateHostParamsInternal` fee-token migration can be permanently griefed with a 1-wei transfer - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.updateHostParamsInternal` refuses to switch the configured `feeToken` unless the host's current balance of the old fee token is exactly zero. Because ERC-20 transfers are permissionless, any unprivileged address can top up the host's fee-token balance by 1 wei at any time, which makes this check fail and blocks the governance-driven fee-token migration indefinitely — the same bug class as the reported `getTVLByOwnerOfShares == 0` DoS in `SuperVaultStrategy`.

### Finding Description
`updateHostParamsInternal` enforces:
```solidity
address oldFeeToken = feeToken();
if (oldFeeToken != address(0) && oldFeeToken != params.feeToken) {
    uint256 balance = IERC20(oldFeeToken).balanceOf(address(this));
    if (balance != 0) revert CannotChangeFeeToken();
}
``` [1](#0-0) 

This function is invoked by `updateHostParams`, gated to `restrict(_hostParams.hostManager)`, i.e. it can only be triggered by the authorized `HostManager` acting on a cross-chain governance message from Hyperbridge (nexus). [2](#0-1) 

The precondition — "the host's balance of the old fee token must be exactly zero" — is exactly the pattern flagged in the external report. It is *not* enforceable against an unprivileged actor: `feeToken` is a standard ERC-20, and `IERC20.transfer(hostAddress, 1)` is callable by anyone, with no allowance or permission needed to push tokens into the host. There is a foundry test confirming the check exists and that a nonzero balance blocks the update:
```solidity
function testSweepFeeTokenBeforeUpdate() public {
    feeToken.mint(address(host), 1 * 1e18);
    ...
    vm.expectRevert(EvmHost.CannotChangeFeeToken.selector);
    host.updateHostParams(params);
    feeToken.burn(address(host), 1 * 1e18);
    // we can set host params
    vm.prank(host.hostParams().admin);
    host.updateHostParams(params);
}
``` [3](#0-2) 

Because the actual `updateHostParams` transaction only lands after a full ISMP round trip from Hyperbridge governance (dispatch → relay → proof verification → execution on the destination EVM chain), an attacker watching the mempool/chain for this governance action has ample time to front-run it (or simply keep the host topped up with 1 wei of the fee token at all times) so that every attempt to complete the migration reverts with `CannotChangeFeeToken`.

### Impact Explanation
This blocks a critical governance operation — rotating away from a compromised, deprecated, or otherwise unwanted fee token — indefinitely, as long as the griefer keeps re-funding a trivial amount of the old fee token to the host contract after each sweep/withdraw attempt. Since `withdraw()` (used to sweep the balance before retrying) is itself also gated behind the same cross-chain-governance round trip via `hostManager`, the griefer's single local transaction (near-zero cost) always wins the race against a multi-block cross-chain governance flow. This is a permanent freezing of a governance capability that guards a chain-wide protocol parameter, satisfying the Medium-risk "route unable to deliver messages" / DoS-of-governance class from the rules.

### Likelihood Explanation
High: the only requirement is being able to call `IERC20.transfer` on the (public) fee-token contract, which any address can do without prior state, permission, or cost beyond gas and 1 wei of the token. No compromised keys or special access are required — this is reachable from a single unprivileged transaction, matching the reachability bar (a submitted transaction) required by the validation rules.

### Recommendation
Remove the strict `balance != 0` revert from `updateHostParamsInternal`, or replace it with a mechanism that does not depend on an externally-manipulable balance — for example, automatically sweeping/burning the residual old-fee-token balance as part of the same governance call (moving it to the beneficiary or simply ignoring dust) instead of requiring it be pre-drained to exactly zero before the swap can proceed.

### Proof of Concept
1. Governance (via Hyperbridge/nexus) begins the process of rotating `feeToken` from `A` to `B` by dispatching a `SetHostParam` governance request that will eventually call `host.updateHostParams(params)` with `params.feeToken = B`.
2. Before that message is relayed and finalized on the EVM chain, an attacker calls `IERC20(A).transfer(address(host), 1)` — a fully permissionless action.
3. When the governance message is finally delivered and `HostManager.onAccept` invokes `updateHostParams`, `updateHostParamsInternal` computes `balance = IERC20(A).balanceOf(address(host)) = 1`, and reverts with `CannotChangeFeeToken`.
4. Governance must dispatch another cross-chain message to `withdraw()` the 1 wei, then retry `updateHostParams` — but the attacker can repeat step 2 before that retry lands, indefinitely blocking the fee-token migration at negligible cost.

### Citations

**File:** evm/src/core/EvmHost.sol (L564-575)
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
