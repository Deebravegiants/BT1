# [H] Tap payments inconsistency

## Summary
Severity: High
Source: https://github.com/AragonBlack/fundraising/blob/master/apps/tap/contracts/Tap.sol
Type: audit-issue

## Details
#### Description

Every time project managers want to withdraw tapped funds, the maximum amount of withdrawable funds is calculated in `tap._maximumWithdrawal` function. The method ensures that project managers can only withdraw unlocked funds (balance exceeding the collaterals `minimum` comprised of the collaterals configured `floor` including the minimum tokens to `hold`) even though their allowance might be higher.
 
1. if there are **no** unlocked funds available, the maximum withdrawal is zero (`balance <= minimum`).
2. if there are unlocked funds available (`balance > minimum`) and the allowance (`tapped`) would result in a `balance >= minimum`, the maximum withdrawal amount is the calculated allowance `tapped`.
3. if there are unlocked funds available (`balance > minimum`) and the allowance (`tapped`) would result in a `balance < minimum`, the maximum withdrawal amount `tapped` is capped to `balance - minimum` to ensure that the remaining collateral `balance` is at least at the `minimum` and not below.

This means that in the case of (3) if there are not enough funds to withdraw [`tapped`](https://github.com/AragonBlack/fundraising/blob/master/apps/tap/contracts/Tap.sol)(`time*tap_rate`) amount of tokens, it gets truncated and only a part of tapped tokens gets withdrawn. 


**code/apps/tap/contracts/Tap.sol:L239-L255**
```solidity
function _maximumWithdrawal(address _token) internal view returns (uint256) {
    uint256 toBeClaimed = controller.collateralsToBeClaimed(_token);
    uint256 floor = floors[_token];
    uint256 minimum = toBeClaimed.add(floor);
    uint256 balance = _token == ETH ? address(reserve).balance : ERC20(_token).staticBalanceOf(reserve);
    uint256 tapped = (_currentBatchId().sub(lastWithdrawals[_token])).mul(rates[_token]);

    if (minimum >= balance) {
        return 0;
    }

    if (balance >= tapped.add(minimum)) {
        return tapped;
    }

    return balance.sub(minimum);
}
```

The problem is that the remaining tokens  (`tapped - capped_tapped`) cannot be claimed afterward and `tapped` value is reset to zero.

#### Remediation

In case the maximum withdrawal amount gets capped, the information about the remaining tokens that the project team should have been able to withdraw should be kept to allow them to withdraw the tokens at a later point in time when there are enough funds for it.
