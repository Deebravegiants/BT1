### Title
DoS of `EvmHost.updateHostParams` fee-token migration via griefing donation - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.updateHostParamsInternal` blocks a fee-token migration if the host's current `IERC20` balance of the outgoing fee token is non-zero. Because any unprivileged account can transfer even a single unit of that token directly to the `EvmHost` contract address, this check can be permanently forced to fail, making the fee-token migration governance action permanently unusable — the same bug class as the reported `RioLRTAssetRegistry.removeAsset` DOS, where a balance check gating a state-changing action is griefable by an unprivileged direct token transfer.

### Finding Description
`updateHostParamsInternal` is the internal logic invoked by `updateHostParams`, which is restricted to the `hostManager` (cross-chain governance): [1](#0-0) 

Within it, when governance attempts to change the configured fee token, the function requires the host's balance of the *old* fee token to be exactly zero: [2](#0-1) 

`feeToken()` is an arbitrary configured `IERC20` (e.g. a stablecoin used to pay dispatch/relayer fees). Any account — including an unprivileged party with no special role, such as a relayer, bandwidth purchaser, or general token holder — can call `IERC20(oldFeeToken).transfer(address(host), 1)` at any time. Because `balanceOf(address(this))` reflects raw ERC20 balance regardless of accounted/escrowed amounts, this single transfer permanently sets `balance != 0`, causing every future `updateHostParams` call that attempts to change the fee token to revert with `CannotChangeFeeToken()` — for as long as the attacker (or anyone) keeps re-donating dust after any governance sweep attempt (there is no path in `EvmHost` to zero out this balance other than `withdraw`, which is itself restricted to `hostManager` and pulls the full balance to a beneficiary rather than "cleaning" it to permit migration in the same transaction as `updateHostParams`).

This mirrors the reported bug class exactly: a `balance == 0` invariant used to gate an authorized state-transition function, where the balance is influenced by unrestricted, permissionless ERC20 transfers into the target contract, rather than by internal, accounted state.

### Impact Explanation
If the currently configured fee token becomes compromised, depegged, deprecated, or otherwise needs replacement, cross-chain governance's only path to migrate it (`updateHostParams`) can be permanently blocked by any unprivileged actor sending a trivial amount of the old fee token to the `EvmHost` contract. This freezes the protocol's ability to safely rotate its fee token, forcing continued reliance on a token governance has determined must be replaced — a permanent freeze of protocol configuration functionality directly reachable and triggerable by an unprivileged party from a single transaction.

### Likelihood Explanation
Trivially likely: the attack requires only holding (or acquiring) a minimal amount of the current fee token and sending it to the well-known `EvmHost` address — no special permissions, timing, or cost beyond gas and a dust amount of the fee token. It can be repeated indefinitely to counter any attempted remediation.

### Recommendation
Do not gate fee-token migration on the raw `balanceOf` of the contract. Instead:
- Track internally accounted/escrowed fee-token balances (e.g., pending relayer fees, request commitments) separately from raw token balance, and check that accounted value instead of `IERC20.balanceOf(address(this))`.
- Alternatively, when migrating fee tokens, atomically sweep the old fee token's balance (as `withdraw` does) to a beneficiary as part of `updateHostParamsInternal` rather than reverting, so a griefing donation cannot block the migration.

### Proof of Concept
1. `EvmHost` is deployed with `feeToken = TokenA`.
2. Governance decides to migrate to `TokenB` and prepares to call `updateHostParams` with `params.feeToken = TokenB`.
3. Before that transaction lands, any unprivileged account calls `TokenA.transfer(address(evmHost), 1)`.
4. Governance's `updateHostParams` call now hits: [2](#0-1) 
   `balance = 1 != 0` → reverts with `CannotChangeFeeToken()`.
5. The attacker repeats step 3 after any `withdraw` sweep attempt, indefinitely blocking the fee-token migration.

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
