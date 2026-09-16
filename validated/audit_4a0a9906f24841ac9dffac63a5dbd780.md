This is exactly the same bug class as the MultiRewards `periodFinish` DoS: an unprivileged, permissionless call that repeatedly extends a lock/timer, permanently blocking a privileged recovery action that depends on that timer expiring. In Hyperbridge, this is `SimplexPaymaster.addStake` on the ERC-4337 `EntryPoint`, which is gated only to be treasury-only per the documented fix, but the underlying `EntryPoint` mechanics mean *any* caller sending even 1 wei can re-arm the lock unless `addStake` itself is fully restricted everywhere it's reachable.

### Title
Permissionless `addStake` can perpetually extend the EntryPoint unstake delay and block stake recovery - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster` must stay staked with the ERC-4337 `EntryPoint` for bundlers to accept its storage access. The `EntryPoint.addStake(uint32 _unstakeDelaySec)` primitive only ever increases `unstakeDelaySec` and resets any pending unlock timer on every call, regardless of the amount staked (even 1 wei). If any code path allows an unprivileged caller to invoke `addStake` on the paymaster, that caller can push `unstakeDelaySec` to its `uint32` maximum (~136 years) and cancel any pending `unlockStake()` countdown indefinitely, permanently preventing the treasury-only `unlockStake()`/`withdrawStake()` recovery path from ever completing — exactly the `periodFinish`-style DoS in the external report, but against stake recovery instead of `rewardsDuration`.

### Finding Description
`SimplexPaymaster` is required to keep a stake with the `EntryPoint` (`ENTRYPOINT_V08`) for bundler acceptance [1](#0-0) . The documented fix for this exact class of bug states: “Gating `addStake` is the half that cannot be deferred. The EntryPoint only ever lets `unstakeDelaySec` grow and resets any pending unlock on every `addStake`, so while the function is open an unprivileged caller can push the delay to 136 years and cancel unlocks indefinitely — which would defeat the recovery path being added here” [2](#0-1) .

The regression fork test explicitly demonstrates the attack primitive still reachable at the `EntryPoint` level: "`addStake` itself is permissionless, so anyone can also extend the unstake delay," and a griefer using only `1 wei` extends the delay past a century on the live deployed paymaster address [3](#0-2) . The same test file also asserts that no privileged identity — not the treasury, not the host, not the `EntryPoint`, not an arbitrary caller — can call `unlockStake()`/`withdrawStake()` successfully on the live fork, i.e. the stake is *currently* permanently locked in production on BSC and Ethereum mainnet deployments [4](#0-3) .

This maps directly to the MultiRewards `periodFinish` bug class: a public/permissionless function (`addIncentives`/`notifyRewardAmount` in the original report; `EntryPoint.addStake` reachable through the paymaster or directly against the paymaster's stake account) advances a timer/lock state variable with no floor on contribution size (1 wei is sufficient in both cases), and that advance permanently blocks a privileged operation (`updateRewardsDurationForVault` in the original; `unlockStake`/`withdrawStake` here) that requires the timer to have elapsed.

### Impact Explanation
If any unrestricted path to `addStake` exists against the live paymaster's `EntryPoint` stake account (which the fork test proves is exploitable with 1 wei of value on a currently-staked, currently-deployed paymaster), the treasury's governance-gated stake-recovery flow (`UnlockStake`/`WithdrawStake`, added specifically to remedy stake being otherwise unrecoverable) can be permanently defeated. The stake amounts observed on the live forks are non-trivial ("live stake at risk (wei)") and would become permanently frozen, unrecoverable funds — meeting the "permanent freezing of funds" bar.

### Likelihood Explanation
High. `addStake` on the `EntryPoint` accepts any caller and any non-zero value (as low as 1 wei), and resets the unlock timer on every call unconditionally — there is no economic disincentive since griefing costs the attacker almost nothing while indefinitely locking the paymaster's real stake, mirroring the "even 1 wei" griefing vector described in the original MultiRewards report.

### Recommendation
Ensure `addStake` cannot be invoked by any unprivileged account against the paymaster's `EntryPoint` stake account under any code path (the documented fix already restricts the paymaster's own `addStake` wrapper to the treasury) and audit for any other entry point — direct calls to the `EntryPoint` referencing the paymaster's address, fallback/receive handling, or other contracts — that could still trigger `addStake` on the paymaster's behalf. Consider also enforcing a minimum stake delta or requiring `unlockStake` state to be preserved across `addStake` calls, consistent with the recommendation in the original report to remove/rework unconditional timer-advancement logic.

### Proof of Concept
The existing regression test in the repo demonstrates the primitive against the live deployed contract: [5](#0-4) 
A `griefer` account with no privileges calls `paymaster.addStake{value: 1 wei}(type(uint32).max)` and the unstake delay jumps from its prior value to beyond 100 years, while every privileged caller (`treasury`, `host`, `ENTRY_POINT`, and an arbitrary address) is refused when calling `unlockStake()`/`withdrawStake()` [6](#0-5) , confirming stake recovery is currently blocked on the live BSC/Ethereum deployments referenced by the fork test addresses.

### Citations

**File:** evm/tests/foundry/SimplexPaymasterStakeLockForkTest.t.sol (L1-34)
```text
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Test} from "forge-std/Test.sol";
import {ERC4337Utils} from "@openzeppelin/contracts/account/utils/draft-ERC4337Utils.sol";

interface ISimplexPaymasterLive {
    function treasury() external view returns (address);

    function host() external view returns (address);

    function addStake(uint32 unstakeDelaySec) external payable;

    function unlockStake() external;

    function withdrawStake(address payable to) external;

    function withdraw(address payable to, uint256 value) external;
}

interface IEntryPointStakeView {
    function getDepositInfo(address account)
        external
        view
        returns (uint256 deposit, bool staked, uint112 stake, uint32 unstakeDelaySec, uint48 withdrawTime);
}

/// @notice Against the LIVE deployed paymasters: once native is staked with the EntryPoint,
///         no caller and no governance action can ever recover it, because every unlock path
///         routes through `_authorizeWithdraw()`, which reverts unconditionally, and the
///         governance `RequestKind` enum has no stake variant. `addStake` itself is
///         permissionless, so anyone can also extend the unstake delay.
contract SimplexPaymasterStakeLockForkTest is Test {
    IEntryPointStakeView constant ENTRY_POINT = IEntryPointStakeView(address(ERC4337Utils.ENTRYPOINT_V08));
```

**File:** evm/tests/foundry/SimplexPaymasterStakeLockForkTest.t.sol (L46-81)
```text
    function testLiveBscStakeIsPermanentlyLocked() public {
        if (!_setUpFork("BSC_FORK_URL", 0xeD02f9f0df8F562B89cC5b25867Ad3C2d61252A9)) return;
        _assertStakeUnrecoverable();
    }

    function testLiveEthereumStakeIsPermanentlyLocked() public {
        if (!_setUpFork("MAINNET_FORK_URL", 0xD4340d7466e040626383cb9cda9307ba8E081149)) return;
        _assertStakeUnrecoverable();
    }

    function _assertStakeUnrecoverable() internal {
        (, bool staked, uint112 stake,,) = ENTRY_POINT.getDepositInfo(address(paymaster));
        assertTrue(staked, "precondition: live paymaster is staked");
        assertGt(stake, 0, "precondition: stake is non-zero");
        emit log_named_uint("live stake at risk (wei)", stake);

        address treasury = paymaster.treasury();
        address host = paymaster.host();

        // Every privileged identity in the system is refused.
        address[4] memory callers = [treasury, host, address(ENTRY_POINT), makeAddr("anyone")];
        for (uint256 i = 0; i < callers.length; i++) {
            vm.prank(callers[i]);
            vm.expectRevert();
            paymaster.unlockStake();

            vm.prank(callers[i]);
            vm.expectRevert();
            paymaster.withdrawStake(payable(callers[i]));
        }

        // Stake is still there, and still locked.
        (, bool stakedAfter, uint112 stakeAfter,,) = ENTRY_POINT.getDepositInfo(address(paymaster));
        assertTrue(stakedAfter);
        assertEq(stakeAfter, stake, "stake unchanged: no recovery path exists");
    }
```

**File:** evm/tests/foundry/SimplexPaymasterStakeLockForkTest.t.sol (L83-101)
```text
    /// `addStake` is permissionless, so a griefer can both lock fresh value into the
    /// contract and stretch the unstake delay a future upgrade would have to wait out.
    function testAnyoneCanAddStakeAndExtendTheUnstakeDelay() public {
        if (!_setUpFork("BSC_FORK_URL", 0xeD02f9f0df8F562B89cC5b25867Ad3C2d61252A9)) return;

        (,,, uint32 delayBefore,) = ENTRY_POINT.getDepositInfo(address(paymaster));
        address griefer = makeAddr("griefer");
        vm.deal(griefer, 1 ether);

        vm.prank(griefer);
        paymaster.addStake{value: 1 wei}(type(uint32).max);

        (,, uint112 stakeAfter, uint32 delayAfter,) = ENTRY_POINT.getDepositInfo(address(paymaster));
        emit log_named_uint("unstake delay before (s)", delayBefore);
        emit log_named_uint("unstake delay after  (s)", delayAfter);
        assertGt(delayAfter, delayBefore, "an unprivileged caller extended the unstake delay");
        assertGt(uint256(delayAfter), 100 * 365 days, "delay pushed beyond a century");
        assertGt(stakeAfter, 0);
    }
```

**File:** sdk/packages/simplex/docs/ai/decisions/2026-08-19-stake-gets-a-governance-recovery-path-and-addstake-is-treasury.md (L1-7)
```markdown
# 2026-08-19 — Stake gets a governance recovery path, and `addStake` is treasury-only (#1071)

Chosen: two new empty-payload request kinds (`UnlockStake` = 5, `WithdrawStake` = 6, always paying out to the treasury) and an `addStake` override gated to the treasury.

The alternative — leave stake unrecoverable and simply never stake — is not available: bundlers require a staked paymaster for the storage access this contract performs, so staking is effectively mandatory and was already done on three chains. Two kinds rather than one because the EntryPoint requires `unlockStake()` and then a wait of `unstakeDelaySec` before `withdrawStake()` will succeed; a single request could not span that delay.

Gating `addStake` is the half that cannot be deferred. The EntryPoint only ever lets `unstakeDelaySec` grow and resets any pending unlock on every `addStake`, so while the function is open an unprivileged caller can push the delay to 136 years and cancel unlocks indefinitely — which would defeat the recovery path being added here.
```
