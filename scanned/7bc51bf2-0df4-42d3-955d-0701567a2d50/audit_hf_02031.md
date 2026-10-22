# [M] Possible Costly xMPH From Improper Liquidity Initialization

## Summary
Severity: Medium
Contest weight: 0.4630
Dataset id: 11571
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The 88mph-v3 protocol allows users to stake supported MPH and get in return xMPH tokens to represent the pool share. While examining the share calculation with the given deposits, we notice an issue that may unnecessarily make the pool token extremely expensive and bring hurdles (or even causes loss) for later depositors.
To elaborate, we show below the deposit()/withdraw() routines. The deposit() routine is used for participating users to deposit the supported asset (e.g., MPH) and get respective xMPH pool tokens in return. The issue occurs when the pool is being initialized under the assumption that the current pool is empty.
```solidity
function deposit(uint256 _mphAmount)
external returns (uint256 shareAmount) {
    require(_mphAmount > 0, "xMPH: 0 amount");
    shareAmount = _mphAmount.decdiv(getPricePerFullShare());
    _mint(msg.sender, shareAmount);
    mph.transferFrom(msg.sender, address(this), _mphAmount);
}

/**
 * @notice Withdraw MPH using xMPH
 * @dev The amount can't be 0
 * @param _shareAmount The amount of xMPH to burn
 * @return mphAmount The amount of MPH withdrawn
 */
function withdraw(uint256 _shareAmount)
external returns (uint256 mphAmount) {
    require(_shareAmount > 0, "xMPH: 0 amount");
    mphAmount = _shareAmount.decmul(getPricePerFullShare());
    _burn(msg.sender, _shareAmount);
    mph.transfer(msg.sender, mphAmount);
}

/**
 * @notice Compute the amount of MPH that can be withdrawn burning 1 xMPH. Increases linearly during a reward distribution period.
 * @dev Initialized to be PRECISION (representing 1 MPH = 1 xMPH)
 * @return The amount of MPH that can be withdrawn burning 1 xMPH
 */
function getPricePerFullShare()
public view returns (uint256) {
    uint256 totalShares = totalSupply();
    uint256 mphBalance = mph.balanceOf(address(this));
    if (totalShares == 0 || mphBalance == 0) {
        return PRECISION;
    }
    uint256 _lastRewardAmount = lastRewardAmount;
    uint256 _currentUnlockEndTimestamp = currentUnlockEndTimestamp;
    if (_lastRewardAmount == 0 || block.timestamp >= _currentUnlockEndTimestamp) {
        // no rewards or rewards fully unlocked
        // entire balance withdrawable
        return mphBalance.decmul(totalShares);
    } else {
        // rewards not fully unlocked
        // deduct locked rewards from balance
        uint256 _lastRewardTimestamp = lastRewardTimestamp;
        uint256 lockedRewardAmount =
        (_lastRewardAmount * (_currentUnlockEndTimestamp - block.timestamp))
        / (_currentUnlockEndTimestamp - _lastRewardTimestamp);
        return (mphBalance - lockedRewardAmount).decmul(totalShares);
    }
}
```
Specifically, when the pool is being initialized (line 108), the share value directly takes the value of _mphAmount.decdiv(PRECISION) (line 77), which is manipulatable by the malicious actor. As this is the first deposit, the current total supply equals the calculated shareAmount = 1 WEI. With that, the actor can further deposit a huge amount of MPH with the goal of making the xMPH pool token extremely expensive.
An extremely expensive xMPH pool token can be very inconvenient to use as a small number of 1 WEI may denote a large value. Furthermore, it can lead to precision issue in truncating the computed pool tokens for deposited assets. If truncated to be zero, the deposited assets are essentially considered dust and kept by the pool without returning any pool tokens.
This is a known issue that has been mitigated in popular Uniswap. When providing the initial liquidity to the contract (i.e. when totalSupply is 0), the liquidity provider must sacrifice 1000 LP tokens (by sending them to address(0)). By doing so, we can ensure the granularity of the LP tokens is always at least 1000 and the malicious actor is not the sole holder. This approach may bring an additional cost for the initial liquidity provider, but this cost is expected to be low and acceptable.

## Recommendation
Revise current execution logic of getPricePerFullShare() to defensively calculate the share amount when the pool is being initialized. An alternative solution is to ensure guarded launch that safeguards the first deposit to avoid being manipulated.
