### Title
`KernelDepositPool.stakeFor` Applies `updateReward(msg.sender)` Instead of `updateReward(_account)`, Causing Reward Over-Accrual for Users Staking via `KernelMerkleDistributor.claimAndStake` - (File: contracts/KERNEL/KernelDepositPool.sol)

---

### Summary

`KernelDepositPool.stakeFor` is decorated with `updateReward(msg.sender)`. When invoked by `KernelMerkleDistributor.claimAndStake`, `msg.sender` is the distributor contract, not the beneficiary `_account`. The beneficiary's `userRewardPerTokenPaid` is therefore never checkpointed at the moment their balance grows, so they retroactively accrue rewards from an earlier point in time — stealing yield from every other staker.

---

### Finding Description

`KernelDepositPool` implements a standard Synthetix-style staking reward model. The `updateReward` modifier snapshots the global `rewardPerTokenStored` and then, for the supplied address, writes:

```
rewards[addr]               = earned(addr)
userRewardPerTokenPaid[addr] = rewardPerTokenStored
```

This checkpoint is the only mechanism that prevents a staker from claiming rewards that accrued before they deposited.

`stake` correctly passes `msg.sender` (the depositor) to the modifier:

```solidity
// KernelDepositPool.sol line 281
function stake(uint256 _amount) external nonReentrant updateReward(msg.sender) {
```

`stakeFor`, however, also passes `msg.sender` — which is the *caller*, not the beneficiary:

```solidity
// KernelDepositPool.sol lines 296-300
function stakeFor(
    address _account,
    uint256 _amount
)
    external
    nonReentrant updateReward(msg.sender)
```

`KernelMerkleDistributor.claimAndStake` is the primary caller of `stakeFor`:

```solidity
// KernelMerkleDistributor.sol lines 270-285
function claimAndStake(
    uint256 index,
    address account,
    uint256 cumulativeAmount,
    bytes32[] calldata merkleProof
)
    external
    nonReentrant
    whenNotPaused
{
    uint256 amountToStake = _processClaim(index, account, cumulativeAmount, merkleProof);
    IKernelDepositPool(kernelDepositPool).stakeFor(account, amountToStake);
    emit ClaimedAndStaked(index, account, amountToStake);
}
```

When this executes:

1. `updateReward(KernelMerkleDistributor)` runs — it checkpoints the *distributor's* reward state, not the user's.
2. `balanceOf[account] += amountToStake` — the user's balance grows.
3. `userRewardPerTokenPaid[account]` is **never written** — it remains at whatever stale value it held before (zero for a first-time staker).

Consequently, `earned(account)` computes:

```
rewards[account] + balanceOf[account] * (rewardPerToken() - userRewardPerTokenPaid[account]) / 1e18
```

With `userRewardPerTokenPaid[account] == 0`, the user earns rewards as if they had been staked since the very first reward distribution, regardless of when they actually called `claimAndStake`.

---

### Impact Explanation

Every unit of retroactive reward claimed by the over-accruing user is a unit that cannot be claimed by legitimate stakers who were present during that earlier period. The reward pool is finite; the over-accrual is a direct, proportional transfer of yield away from honest stakers. This satisfies **High — Theft of unclaimed yield**.

---

### Likelihood Explanation

`claimAndStake` is a first-class, publicly advertised function of `KernelMerkleDistributor`. Any user who prefers the gas-efficient single-transaction path over `claim` + `stake` triggers the bug. No special permissions, timing, or adversarial setup is required. The only prerequisite is that at least one reward distribution has occurred before the user calls `claimAndStake` — a near-certain condition in any live deployment.

---

### Recommendation

Change the modifier argument in `stakeFor` from `msg.sender` to `_account`:

```solidity
function stakeFor(
    address _account,
    uint256 _amount
)
    external
    nonReentrant
-   updateReward(msg.sender)
+   updateReward(_account)
{
```

This ensures the beneficiary's reward checkpoint is written at the moment their balance increases, exactly as `stake` does for a direct depositor.

---

### Proof of Concept

1. Reward distribution begins; `rewardPerTokenStored` grows to value `R`.
2. Alice stakes 1 000 KERNEL directly via `stake`. Her `userRewardPerTokenPaid[Alice] = R`.
3. More rewards accumulate; `rewardPerToken()` rises to `2R`.
4. Bob calls `claimAndStake(index, Bob, amount, proof)`.
   - `_processClaim` succeeds; `amountToStake = 1 000 KERNEL`.
   - `kernelDepositPool.stakeFor(Bob, 1_000e18)` is called.
   - `updateReward(KernelMerkleDistributor)` runs — Bob's state is untouched.
   - `balanceOf[Bob] += 1_000e18`; `userRewardPerTokenPaid[Bob]` remains `0`.
5. Bob immediately calls `getReward`.
   - `earned(Bob) = 0 + 1_000e18 * (2R - 0) / 1e18 = 2_000 * R_units`.
   - Bob collects rewards as if he had staked since the very beginning.
   - Alice's share of the reward pool is diluted by the amount Bob illegitimately claimed. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L232-242)
```text
    modifier updateReward(address _account) {
        rewardPerTokenStored = rewardPerToken();
        updatedAt = lastTimeRewardApplicable();

        if (_account != address(0)) {
            rewards[_account] = earned(_account);
            userRewardPerTokenPaid[_account] = rewardPerTokenStored;
        }

        _;
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L281-289)
```text
    function stake(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();

        balanceOf[msg.sender] += _amount;
        totalKernelStaked += _amount;
        kernelToken.safeTransferFrom(msg.sender, address(this), _amount);

        emit Staked(msg.sender, _amount);
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L296-300)
```text
    function stakeFor(
        address _account,
        uint256 _amount
    )
        external
```

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L270-285)
```text
    function claimAndStake(
        uint256 index,
        address account,
        uint256 cumulativeAmount,
        bytes32[] calldata merkleProof
    )
        external
        nonReentrant
        whenNotPaused
    {
        uint256 amountToStake = _processClaim(index, account, cumulativeAmount, merkleProof);

        IKernelDepositPool(kernelDepositPool).stakeFor(account, amountToStake);

        emit ClaimedAndStaked(index, account, amountToStake);
    }
```
