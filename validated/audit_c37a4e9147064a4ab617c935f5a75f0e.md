## Title
Streamed yield can be captured by an unrelated depositor when `totalSupply` drops to zero mid-vest — ([File: sdk/packages/core/contracts/vaults/StreamingYieldVault.sol])

### Summary
`StreamingYieldVault` unlocks a yield tranche purely as a function of elapsed `block.timestamp`, exactly like `VirtualStakingRewards.rewardRate` unlocks purely as a function of elapsed time. The audited bug arises because the reward math assumes a constant, non-zero pool of participants (`_totalSupply`) for the whole distribution window; when that assumption breaks (`_totalSupply == 0`), value is misallocated instead of going to the intended recipients. `StreamingYieldVault` has the same time-only unlock design but does not prevent `totalSupply` (shares outstanding) from dropping to zero mid-vest, since only `maxDeposit`/`maxMint` are gated — `withdraw`/`redeem` are not.

### Finding Description
`_lockedYield()` computes the still-locked portion of a tranche purely from `block.timestamp - _vestingStart`, independent of how many shares currently exist: [1](#0-0) 

Only deposits/mints are blocked while a tranche vests; withdrawals and redemptions are never restricted: [2](#0-1) 

This means all existing shareholders can fully redeem during an active vesting window, driving `totalSupply()` to `0` while `_vestingAmount`/`_vestingStart` are still counting down. The vesting math keeps running regardless: `_lockedYield()` keeps shrinking with time, so `totalAssets()` (which is `balanceOf(vault) - _lockedYield()`) keeps rising even though there is no one holding shares to claim it: [3](#0-2) 

Once the tranche finishes vesting (or even mid-vest for the unlocked slice), the vault sits with real, unlocked/unlocking assets and zero shares outstanding. `maxDeposit`/`maxMint` reopen as soon as `_isVesting()` is false, and the ERC-4626 first-deposit math (protected only by the constant `DECIMALS_OFFSET` virtual-share offset, not by tying new deposits to the vault's actual pre-existing balance) mints the next depositor shares priced off `totalAssets()`/`totalSupply()+10**offset`. Because `totalSupply == 0`, the *next* depositor's shares absorb a proportional share of the residual unlocked yield that was never backed by their own capital — value that rightfully belonged to the previous shareholders who exited (or was donated by the owner via `addYield`/`onTransferReceived` for those specific shareholders) is instead captured by an unrelated party who simply times a deposit into the empty-supply window.

This is the structural analog of the `VirtualStakingRewards.rewardPerToken()` bug: both contracts run a reward/yield-rate accrual keyed to elapsed time without accounting for `totalSupply == 0`, so value that was supposed to be attributed proportionally to stakers/shareholders present during accrual instead is stranded and then grabbed by whoever is present when accounting resumes.

### Impact Explanation
Real ERC20 assets — the owner's `addYield` donation intended for the shareholders present during that tranche — end up backing shares minted to an unrelated address that deposits after the vault's `totalSupply` incidentally reaches zero. This is a concrete transfer of value away from its intended recipients (theft-like misallocation) reachable by any unprivileged actor who deposits at the right time; no privileged role is required to trigger or exploit it (full withdrawal by existing LPs is a normal, permissionless action).

### Likelihood Explanation
Reaching `totalSupply == 0` mid-vest requires all current shareholders to redeem while a tranche is vesting, which is unrestricted and can happen naturally (e.g., a single LP vault, or coordinated exit) or be induced by a griefer already holding all shares. Once `totalSupply` is zero, any address watching the vault (trivial with public on-chain state) can time a deposit to capture the freed-up yield the moment `maxDeposit` reopens. This does not require MEV-level sophistication beyond normal front-running/monitoring.

### Recommendation
Do not let `_lockedYield()`/vesting accrual continue unconditionally when `totalSupply() == 0`. Options: pause the vesting clock (freeze `_vestingStart` progress) whenever `totalSupply()` is zero and resume it only once shares exist again, or block withdrawals that would bring `totalSupply` to zero while a tranche is actively vesting, mirroring the recommendation to only distribute rewards while participants exist.

### Proof of Concept
1. Owner calls `addYield(amount)`, starting a `VEST` tranche while `totalSupply() > 0` (one or more LPs hold shares).
2. All existing LPs call `redeem`/`withdraw` for their full share balance — this is unrestricted since `maxDeposit`/`maxMint` are the only vesting-gated functions, not `withdraw`/`redeem` (`sdk/packages/core/contracts/vaults/StreamingYieldVault.sol:127-139`). `totalSupply()` becomes `0`, but the vault still holds `balanceOf(vault) == lockedYield` in unvested assets.
3. Time passes; `_lockedYield()` continues shrinking purely as a function of `block.timestamp` (`sdk/packages/core/contracts/vaults/StreamingYieldVault.sol:165-170`), so `totalAssets()` rises with no shares outstanding to claim it.
4. Once `_isVesting()` returns false (or even before, since deposits are blocked only strictly during vesting), an unrelated attacker deposits a small amount. `maxDeposit`/`maxMint` are open (`totalSupply==0`), and ERC4626's conversion formula mints them shares priced against the now-inflated `totalAssets()`/near-zero `totalSupply()`, letting them redeem later for a proportional slice of the previously-locked yield they never contributed capital toward.

### Citations

**File:** sdk/packages/core/contracts/vaults/StreamingYieldVault.sol (L92-96)
```text
    /// @inheritdoc ERC4626
    /// @notice Total assets backing shares, net of any not-yet-vested yield.
    function totalAssets() public view override returns (uint256) {
        return IERC20(asset()).balanceOf(address(this)) - _lockedYield();
    }
```

**File:** sdk/packages/core/contracts/vaults/StreamingYieldVault.sol (L127-139)
```text
    /// @inheritdoc ERC4626
    /// @dev Zero while a tranche is vesting so deposits are closed (and integrators can detect it);
    ///      unbounded otherwise. This is the single lock that keeps new capital from joining
    ///      mid-tranche: `deposit` reverts at its `maxDeposit` check with `ERC4626ExceededMaxDeposit`.
    function maxDeposit(address) public view override returns (uint256) {
        return _isVesting() ? 0 : type(uint256).max;
    }

    /// @inheritdoc ERC4626
    /// @dev Zero while a tranche is vesting so integrators see mints are closed; unbounded otherwise.
    function maxMint(address) public view override returns (uint256) {
        return _isVesting() ? 0 : type(uint256).max;
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
