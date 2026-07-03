### Title
Anyone Can Force-Stake Another User's KERNEL Tokens via `claimAndStake`, Temporarily Freezing Their Funds - (File: contracts/KERNEL/KernelMerkleDistributor.sol)

---

### Summary

`KernelMerkleDistributor.claimAndStake` accepts an arbitrary `account` parameter without verifying `msg.sender == account`. Any external caller who possesses a valid merkle proof for a victim can force the victim's unclaimed KERNEL tokens to be staked in `KernelDepositPool` (subject to a configurable withdrawal delay of up to 30 days) instead of being sent directly to the victim. Once executed, the victim's `claim` path is permanently closed for that index, and their tokens are locked behind the withdrawal queue.

---

### Finding Description

`KernelMerkleDistributor.claimAndStake` is a public, permissionless function that processes a merkle claim for any `account` address and automatically stakes the resulting tokens via `KernelDepositPool.stakeFor`:

```solidity
// contracts/KERNEL/KernelMerkleDistributor.sol
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
``` [1](#0-0) 

The internal `_processClaim` updates `userClaims[account].lastClaimedIndex` and `userClaims[account].cumulativeAmount`, permanently marking the claim as consumed for that account: [2](#0-1) 

After `claimAndStake` is called by an attacker, the victim's `claim` call reverts with `AlreadyClaimed` because `isClaimed(index, account)` returns `true`. The victim's tokens are now staked in `KernelDepositPool`, where they are subject to the `withdrawalDelay` (up to `MAX_WITHDRAWAL_DELAY = 30 days`): [3](#0-2) 

The victim must call `initiateWithdrawal` and then wait for `unlockTime = block.timestamp + withdrawalDelay` before calling `claimWithdrawal` to recover their tokens: [4](#0-3) 

Note that `KernelDepositPool.stakeFor` is gated by `STAKE_FOR_ROLE`, but `KernelMerkleDistributor` holds this role by design, making the distributor the permissionless entry point for the attack: [5](#0-4) 

By contrast, the direct `claim` function in the same distributor also accepts any `account` but sends tokens directly to `account` — causing no harm. The harm is exclusive to `claimAndStake` because it routes tokens into a time-locked staking contract instead of the user's wallet: [6](#0-5) 

---

### Impact Explanation

**Medium — Temporary freezing of unclaimed yield.**

An attacker can force any user's unclaimed KERNEL tokens into `KernelDepositPool` with a withdrawal delay of up to 30 days. The user loses immediate access to their tokens and must go through the two-step withdrawal process (`initiateWithdrawal` → wait → `claimWithdrawal`). The tokens are not permanently lost, but they are locked for a material duration, preventing the user from selling, transferring, or using them in other protocols during that window.

---

### Likelihood Explanation

**High.** The merkle tree and its proofs are public (off-chain data published by the protocol). Any observer can construct a valid `(index, account, cumulativeAmount, merkleProof)` tuple for any unclaimed account and call `claimAndStake` before the legitimate user does. No special role, capital, or privileged access is required. The attack is cheap (a single transaction) and can be applied to all unclaimed accounts simultaneously.

---

### Recommendation

Add a `msg.sender == account` check in `claimAndStake` to ensure only the account itself (or an explicitly authorized delegate) can trigger the stake-on-claim path:

```solidity
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
    if (msg.sender != account) revert UnauthorizedCaller();
    uint256 amountToStake = _processClaim(index, account, cumulativeAmount, merkleProof);
    IKernelDepositPool(kernelDepositPool).stakeFor(account, amountToStake);
    emit ClaimedAndStaked(index, account, amountToStake);
}
```

Alternatively, mirror the pattern used in `KernelTop100MerkleDistributor.claimAndStake`, which correctly derives `user = msg.sender` and never accepts an external `account` parameter: [7](#0-6) 

---

### Proof of Concept

1. Alice has unclaimed KERNEL tokens in `KernelMerkleDistributor` at `index = 5`, `cumulativeAmount = 1000e18`. The merkle proof is publicly derivable.
2. Attacker calls `claimAndStake(5, alice, 1000e18, aliceProof)`.
3. `_processClaim` validates the proof, computes the claimable delta, and updates `userClaims[alice]` — marking the claim consumed.
4. `kernelDepositPool.stakeFor(alice, delta)` is called; Alice's KERNEL tokens are transferred from the distributor to `KernelDepositPool` and credited to Alice's staking balance.
5. Alice calls `claim(5, alice, 1000e18, aliceProof)` → reverts with `AlreadyClaimed`.
6. Alice must call `initiateWithdrawal(delta)` on `KernelDepositPool`, then wait up to 30 days for `unlockTime`, then call `claimWithdrawal` to recover her tokens.
7. During the entire delay window, Alice's KERNEL tokens are frozen and inaccessible.

### Citations

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L249-266)
```text
    /// @inheritdoc IMerkleDistributor
    function claim(
        uint256 index,
        address account,
        uint256 cumulativeAmount,
        bytes32[] calldata merkleProof
    )
        external
        override
        nonReentrant
        whenNotPaused
    {
        uint256 amountToSend = _processClaim(index, account, cumulativeAmount, merkleProof);

        kernel.safeTransfer(account, amountToSend);

        emit Claimed(index, account, amountToSend);
    }
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

**File:** contracts/KERNEL/KernelMerkleDistributor.sol (L292-310)
```text
    function _processClaim(
        uint256 index,
        address account,
        uint256 cumulativeAmount,
        bytes32[] calldata merkleProof
    )
        internal
        returns (uint256)
    {
        UtilLib.checkNonZeroAddress(account);

        if (currentMerkleRoot == bytes32(0)) {
            revert ZeroValueProvided();
        }

        if (index == 0 || index > currentIndex) {
            revert InvalidIndex();
        }

```

**File:** contracts/KERNEL/KernelDepositPool.sol (L34-36)
```text
    /// @notice The maximum withdrawal delay allowed
    uint256 public constant MAX_WITHDRAWAL_DELAY = 30 days;

```

**File:** contracts/KERNEL/KernelDepositPool.sol (L301-314)
```text
        nonReentrant
        onlyRole(STAKE_FOR_ROLE)
        updateReward(_account)
    {
        UtilLib.checkNonZeroAddress(_account);

        if (_amount == 0) revert AmountZero();

        balanceOf[_account] += _amount;
        totalKernelStaked += _amount;
        kernelToken.safeTransferFrom(msg.sender, address(this), _amount);

        emit StakedFor(msg.sender, _account, _amount);
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L320-338)
```text
    function initiateWithdrawal(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();
        if (balanceOf[msg.sender] < _amount) revert InsufficientStakedBalance();
        if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();

        balanceOf[msg.sender] -= _amount;
        totalKernelStaked -= _amount;

        // Create a withdrawal record
        uint256 withdrawalId = ++withdrawalCounter;
        uint256 unlockTime = block.timestamp + withdrawalDelay;

        withdrawals[withdrawalId] = Withdrawal({
            user: msg.sender, amount: _amount, unlockTime: unlockTime, claimed: false, withdrawalId: withdrawalId
        });
        userWithdrawalIds[msg.sender].push(withdrawalId);

        emit WithdrawalInitiated(msg.sender, _amount, withdrawalId, unlockTime);
    }
```

**File:** contracts/KERNEL/KernelTop100MerkleDistributor.sol (L345-347)
```text
    function claimAndStake(uint256 amount, bytes32[] calldata merkleProof) external nonReentrant whenNotPaused {
        address user = msg.sender;

```
