# [M] `updatePeriod`

## Summary
Severity: Medium
Contest weight: 0.6450
Dataset id: 18618
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the weekly emission routine of the HERMES token contract, specifically in the updatePeriod function that is responsible for minting new tokens each week. The function determines whether additional tokens need to be minted by comparing the contract's current token balance with a calculated required amount that includes the new weekly emission, growth, and the DAO share. The root cause is a logical accounting error: the balance check uses the contract's raw token balance, which may still contain the previous week’s allocation that has not yet been withdrawn by the flywheelGaugeRewards contract because its gaugeCycle can be longer than one week. Consequently, the required amount is underestimated, and the contract may skip minting when it actually needs to create more tokens. An attacker or any user can trigger updatePeriod after a new week has started but before the pending weekly allocation is taken, causing the contract to believe it has sufficient balance and therefore not mint the shortfall. When the gauge later attempts to claim the pending weekly reward, the contract lacks enough HERMES, leading to a shortfall in the distribution. From the user’s perspective this manifests as missing or zero weekly rewards despite the protocol advertising a regular emission; the UI may show that the weekly reward was scheduled but the wallet receives nothing. The impact is a breach of the protocol’s economic guarantees: token holders receive fewer tokens than promised, the DAO receives a reduced share, and overall accounting integrity is compromised. The issue occurs only when the gauge’s withdrawal interval exceeds the weekly period, making it a conditional bug that can be hard to notice because the balance‑check logic appears correct under normal timing. It was discovered during a Code4rena audit through logical analysis of the emission schedule. To remediate, the contract should adjust the required‑balance calculation to account for any pending weekly allocation that remains in the contract, for example by subtracting the outstanding weekly amount from the balance before comparison or by tracking pending rewards in a separate variable. This ensures that the minting logic always creates enough tokens to satisfy both the growth and DAO share obligations, restoring correct accounting and preventing reward shortfalls.

## Proof of Concept
In `updatePeriod()`, mint new `HERMES` every week with a certain percentage of `weeklyEmission`.

The code is as follows:
    
```solidity
function updatePeriod() public returns (uint256) {
    uint256 _period = activePeriod;
    // only trigger if new week
    if (block.timestamp >= _period + week && initializer == address(0)) {
        _period = (block.timestamp / week) * week;
        activePeriod = _period;
        uint256 newWeeklyEmission = weeklyEmission();
        weekly += newWeeklyEmission;
        uint256 _circulatingSupply = circulatingSupply();

        uint256 _growth = calculateGrowth(newWeeklyEmission);
        uint256 _required = _growth + newWeeklyEmission;
        /// @dev share of newWeeklyEmission emissions sent to DAO.
        uint256 share = (_required * daoShare) / base;
        _required += share;
        uint256 _balanceOf = underlying.balanceOf(address(this));          
        if (_balanceOf < _required) {
            HERMES(underlying).mint(address(this), _required - _balanceOf);
        }

        underlying.safeTransfer(address(vault), _growth);

        if (dao != address(0)) underlying.safeTransfer(dao, share);

        emit Mint(msg.sender, newWeeklyEmission, _circulatingSupply, _growth, share);

        /// @dev queue rewards for the cycle, anyone can call if fails
        ///      queueRewardsForCycle will call this function but won't enter
        ///      here because activePeriod was updated
        try flywheelGaugeRewards.queueRewardsForCycle() {} catch {}
    }
    return _period;
}
```

The above code will first determine if the balance of the current contract is less than `_required`. If it is less, then mint new `HERMES`, so that there will be enough `HERMES` for the distribution.

But there is a problem. The current balance of the contract may contain the last `weekly` `HERMES`, that `flywheelGaugeRewards` has not yet taken (e.g. last week’s allocation of `weeklyEmission`).

Because the `gaugeCycle` of `flywheelGaugeRewards` may be greater than one week, it is possible that the last `weekly` `HERMES` has not yet been taken.

So we can’t use the current balance to compare with `_required` directly, we need to consider the `weekly` staying in the contract if it hasn’t been taken, to avoid not having enough balance when `flywheelGaugeRewards` comes to take `weekly`.

## Recommendation
```solidity
function updatePeriod() public returns (uint256) {
    uint256 _period = activePeriod;
    // only trigger if new week
    if (block.timestamp >= _period + week && initializer == address(0)) {
        _period = (block.timestamp / week) * week;
        activePeriod = _period;
        uint256 newWeeklyEmission = weeklyEmission();
        weekly += newWeeklyEmission;
        uint256 _circulatingSupply = circulatingSupply();

        uint256 _growth = calculateGrowth(newWeeklyEmission);
        uint256 _required = _growth + newWeeklyEmission;
        /// @dev share of newWeeklyEmission emissions sent to DAO.
        uint256 share = (_required * daoShare) / base;
        _required += share;
        uint256 _balanceOf = underlying.balanceOf(address(this));          
        if (_balanceOf < weekly + _growth + share ) {
            HERMES(underlying).mint(address(this), weekly + _growth + share - _balanceOf);
        }

        underlying.safeTransfer(address(vault), _growth);

        if (dao != address(0)) underlying.safeTransfer(dao, share);

        emit Mint(msg.sender, newWeeklyEmission, _circulatingSupply, _growth, share);

        /// @dev queue rewards for the cycle, anyone can call if fails
        ///      queueRewardsForCycle will call this function but won't enter
        ///      here because activePeriod was updated
        try flywheelGaugeRewards.queueRewardsForCycle() {} catch {}
    }
    return _period;
}
```
