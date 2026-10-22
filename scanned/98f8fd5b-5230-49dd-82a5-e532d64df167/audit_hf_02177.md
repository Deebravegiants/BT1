# [M] Incentive Inconsistency Between AToken And StableDebtToken

## Summary
Severity: Medium
Contest weight: 0.4035
Dataset id: 12140
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function _mint(address account, uint256 amount) internal virtual {
    require(account != address(0), "ERC20: mint to the zero address");
    _beforeTokenTransfer(address(0), account, amount);
    uint256 currentTotalSupply = _totalSupply.add(amount);
    _totalSupply = currentTotalSupply;
    uint256 accountBalance = _balances[account].add(amount);
    _balances[account] = accountBalance;
    if (address(_getIncentivesController()) != address(0)) {
        _getIncentivesController().handleAction(account, accountBalance, currentTotalSupply);
    }
}

function _mint(
    address account,
    uint256 amount,
    uint256 oldTotalSupply
) internal {
    uint256 oldAccountBalance = _balances[account];
    _balances[account] = oldAccountBalance.add(amount);
    if (address(_incentivesController) != address(0)) {
        _incentivesController.handleAction(account, oldAccountBalance, oldTotalSupply);
    }
}
```

## Recommendation
Be consistent in using the account balance for incentivization measurement.
