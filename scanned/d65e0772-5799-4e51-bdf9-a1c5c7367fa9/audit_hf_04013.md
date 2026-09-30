# [M] SdtRewardReceiver#_withdrawRewards has

## Summary
Severity: Medium
Contest weight: 0.5876
Dataset id: 20419
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _min_dy parameter of poolCvgSDT.exchange is set via the poolCvgSDT.get_dy method. The problem with this is that get_dy is a relative output that is executed at runtime. This means that no matter the state of the pool, this slippage check will never work.
SdtRewardReceiver.sol#L229-L236
```solidity
if (isMint) {
    /// @dev Mint cvgSdt 1:1 via CvgToke contract
    cvgSdt.mint(receiver, rewardAmount);
} else {
    ICrvPoolPlain _poolCvgSDT = poolCvgSDT;
    /// @dev Only swap if the returned amount in CvgSdt is greater than the amount rewarded in SDT
    _poolCvgSDT.exchange(0, 1, rewardAmount, _poolCvgSDT.get_dy(0, 1, rewardAmount), receiver);
}
```
When swapping from SDT to cvgSDT, get_dy is used to set _min_dy inside exchange. The issue is that get_dy is the CURRENT amount that would be received when swapping as shown below:
```solidity
def get_dy(i: int128, j: int128, dx: uint256) -> uint256:
    """
    """
    rates: uint256[N_COINS] = self.rate_multipliers
    xp: uint256[N_COINS] = self._xp_mem(rates, self.balances)
    x: uint256 = xp[i] + (dx * rates[i] / PRECISION)
    y: uint256 = self.get_y(i, j, x, xp, 0, 0)
    dy: uint256 = xp[j] - y - 1
    fee: uint256 = self.fee * dy / FEE_DENOMINATOR
    return (dy - fee) * PRECISION / rates[j]
```
The return value is EXACTLY the result of a regular swap, which is where the problem is. There is no way that the exchange call can ever revert. Assume the user is swapping because the current exchange ratio is 1:1.5. Now assume their withdraw is sandwich attacked. The ratio is change to 1:0.5 which is much lower than expected. When get_dy is called it will simulate the swap and return a ratio of 1:0.5. This in turn doesn't protect the user at all and their swap will execute at the poor price.
SDT rewards will be sandwiched and can lose the entire balance

## Recommendation
Allow the user to set _min_dy directly so they can guarantee they get the amount they want
