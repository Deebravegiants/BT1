## Finding

### Title
Underflow in `StreamingYieldVault.totalAssets()`/`_lockedYield()` freezes all vault funds if the underlying token balance decreases unexpectedly - (File: `sdk/packages/core/contracts/vaults/StreamingYieldVault.sol`)

### Summary
`StreamingYieldVault` computes `totalAssets()` by subtracting `_lockedYield()` from the vault's raw token balance, with no protection against the balance dropping below the locked amount. This is the same bug class as the reported `LibTokenizedVault._accruedInterest()` underflow: the contract assumes the tracked asset balance can never decrease outside of the vault's own accounting (deposit/withdraw/`addYield`), which is not guaranteed for tokens that can be seized, blacklisted, paused-and-clawed-back, or otherwise reduced by the issuer. This vault is live in production (`cNGN → ycNGN` on Base) backed by a "custom upgradeable layout" stablecoin.

### Finding Description
`totalAssets()` is defined as: [1](#0-0) 

and `_lockedYield()` returns the not-yet-vested portion of the active tranche: [2](#0-1) 

The subtraction `balanceOf(vault) - _lockedYield()` is unchecked-safe only under the assumption that `asset.balanceOf(address(this))` can never fall below `_vestingAmount * (VEST - elapsed) / VEST` while a tranche is vesting. The contract's own comments acknowledge this fragile invariant elsewhere (`addYield` pulls funds before arming the tranche specifically "to avoid a transient `totalAssets` underflow"): [3](#0-2) 

However, nothing prevents the vault's balance from decreasing through means outside `addYield`/`withdraw`/`redeem` — e.g., a compliance/blacklist clawback, an admin burn, a token-contract bug/upgrade, or a negative rebase on the underlying asset. Once `balanceOf(vault) < _lockedYield()`, `totalAssets()` reverts with an arithmetic underflow (Solidity ≥0.8 automatically reverts on underflow).

Because `totalAssets()` underlies virtually every ERC-4626 entry point (`deposit`, `mint`, `withdraw`, `redeem`, `convertToShares`, `convertToAssets`, `previewDeposit`, `previewWithdraw`, `maxWithdraw`, `maxRedeem`), a single underflow condition freezes **all** depositors' funds in the vault, not just the balance that was reduced — `withdraw`/`redeem` (which the documentation explicitly states are "always available") become unusable until the tranche fully vests (i.e., `elapsed >= VEST`, which zeroes `_lockedYield()`, per line 168) or forever if the balance never recovers.

The deployment is real: `cNGN → ycNGN (StreamingYieldVault Base)` at `0xa82a3531021317240fb32e67f9c7bc091f737d3b`, backing solver/LP liquidity used to fill Intent Gateway orders: [4](#0-3) 

cNGN is flagged elsewhere in the same config as a "custom upgradeable layout" token, i.e., a proxy-based, potentially regulator-controlled stablecoin (Nigerian Naira pegged) where balance seizure/blacklist/burn actions by the issuer are a realistic, non-malicious-admin external event (this is standard for CBDC-adjacent/regulated stablecoins), not requiring any Hyperbridge-side privileged actor.

### Impact Explanation
If the vault's underlying balance is reduced below the currently locked yield amount (through issuer-side token mechanics outside the vault's control), `totalAssets()` underflows and reverts. This:
- Blocks `withdraw`/`redeem` for every depositor, permanently freezing all funds held in the vault (not just the delta that was removed) until the current tranche's `VEST` window naturally elapses (up to 22 hours) — and reoccurs indefinitely if the deficit persists or a new tranche starts before the deficit clears.
- Also blocks `deposit`/`mint`, compounding the denial of service.
- Directly harms intent solvers/LPs (per `sdk/packages/simplex/...VaultFundingPlanner.ts`) who route idle liquidity through this vault to back Hyperbridge intent fills — an unprivileged, in-scope actor path.

This matches "permanent freezing of funds" in the validated impact categories.

### Likelihood Explanation
Medium: it requires an external event (balance reduction of the underlying token not mediated by the vault) which is plausible but not attacker-controlled from within Hyperbridge contracts themselves. For a regulated/upgradeable stablecoin like cNGN, compliance-driven balance seizure or a rebase/burn mechanic is a realistic operational risk explicitly foreseeable given the token's documented "custom upgradeable layout." The vault's own documentation already warns that "rebasing assets desync the vault's accounting," confirming the underlying assumption is known to be fragile, yet no explicit guard (try/catch, saturating subtraction, or pausing) was implemented.

### Recommendation
Guard the subtraction in `_lockedYield()`/`totalAssets()` so it saturates instead of underflowing, e.g.:
```solidity
function totalAssets() public view override returns (uint256) {
    uint256 bal = IERC20(asset()).balanceOf(address(this));
    uint256 locked = _lockedYield();
    return bal > locked ? bal - locked : 0;
}
```
This mirrors the recommended fix pattern from the referenced report (explicit handling rather than relying on the total/backing value never decreasing), ensuring `withdraw`/`redeem` remain available even if the tracked balance unexpectedly drops, rather than bricking the entire vault.

### Proof of Concept
1. Deploy `StreamingYieldVault` with `cNGN` (or any token capable of an out-of-band balance decrease, e.g., blacklist/seize/burn) as the asset.
2. Owner calls `addYield(amount)`, arming a tranche; `_vestingAmount = amount`, `_vestingStart = block.timestamp`.
3. Before the tranche vests (`block.timestamp < start + VEST`), the token issuer (or a bug/upgrade in the token) reduces the vault's balance such that `balanceOf(vault) < _lockedYield()` (e.g., seizes/burns tokens from the vault address, a legitimate compliance action for a regulated fiat-backed stablecoin).
4. Any user calls `vault.redeem(...)`, `vault.withdraw(...)`, `vault.deposit(...)`, or `vault.previewRedeem(...)` — all revert with an arithmetic underflow inside `totalAssets()`/`_lockedYield()`, because `balanceOf(vault) - _lockedYield()` underflows.
5. All depositors' funds are frozen until `elapsed >= VEST` naturally zeroes `_lockedYield()` (per `sdk/packages/core/contracts/vaults/StreamingYieldVault.sol:168`), or indefinitely if the deficit persists across tranches.

### Citations

**File:** sdk/packages/core/contracts/vaults/StreamingYieldVault.sol (L92-96)
```text
    /// @inheritdoc ERC4626
    /// @notice Total assets backing shares, net of any not-yet-vested yield.
    function totalAssets() public view override returns (uint256) {
        return IERC20(asset()).balanceOf(address(this)) - _lockedYield();
    }
```

**File:** sdk/packages/core/contracts/vaults/StreamingYieldVault.sol (L163-170)
```text
    /// @dev Linear unlock of the current tranche, keyed on `block.timestamp` so that a deposit
    ///      and withdrawal within the same block observe an identical, unchanged share price.
    function _lockedYield() internal view returns (uint256) {
        uint256 start = _vestingStart;
        uint256 elapsed = block.timestamp - start;
        if (elapsed >= VEST) return 0;
        return (_vestingAmount * (VEST - elapsed)) / VEST;
    }
```

**File:** sdk/packages/core/contracts/vaults/StreamingYieldVault.sol (L176-183)
```text
    function addYield(uint256 amount) external onlyOwner {
        // Pull the funds first so `balanceOf` already reflects `amount` before it is marked
        // locked; otherwise `totalAssets` would transiently underflow when a tranche exceeds
        // the current backing (e.g. the very first `addYield` on a near-empty vault).
        IERC20(asset()).safeTransferFrom(msg.sender, address(this), amount);

        _startVesting(amount);
    }
```

**File:** sdk/packages/indexer/src/configs/config-mainnet.json (L205-210)
```json
				"0x46c85152bfe9f96829aa94755d9f915f9b10ef5f": {
					"description": "cNGN \u2192 ycNGN (StreamingYieldVault Base)",
					"vaults": [
						"0xa82a3531021317240fb32e67f9c7bc091f737d3b"
					]
				},
```
