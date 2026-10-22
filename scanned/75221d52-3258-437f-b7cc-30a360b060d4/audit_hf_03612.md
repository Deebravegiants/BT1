# [M] Admin configuration isAllowedForCollateral

## Summary
Severity: Medium
Contest weight: 0.5936
Dataset id: 19639
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the current implementation, after user deposits funds into lending pool and mint lending pool shares, user can call collateralize function to add collateral:
    
```solidity
    function collateralize(uint _posId, address _pool) public virtual onlyAuthorized(_posId) nonReentrant {
        IConfig _config = IConfig(config);
        // check mode status
        uint16 mode = _getPosMode(_posId);
        _require(_config.getModeStatus(mode).canCollateralize, Errors.COLLATERALIZE_PAUSED);
        // check if the position mode supports _pool
        _require(_config.isAllowedForCollateral(mode, _pool), Errors.INVALID_MODE);
        // update collateral on the position
        uint amtColl = IPosManager(POS_MANAGER).addCollateral(_posId, _pool);
        emit Collateralize(_posId, _pool, amtColl);
    }
```

There is a validation:
    
```solidity
    _require(_config.isAllowedForCollateral(mode, _pool), Errors.INVALID_MODE);
```

Let us consider the case:

The mode supports three pools, USDC lending pool, WETH lending pool and a token A lending pool.

The token A is subject to high volatility, the admin decides to disallow token A lending pool added as collateral.

But then the token A is hacked.

The attacker can mint the token A infinitely.

There is a relevant hack in the past:

  1. <https://ciphertrace.com/infinite-minting-exploit-nets-attacker-4-4m/>
Attacker exploited logical and math error to mint token infinitely.

  2. <https://www.coindesk.com/business/2022/10/10/binance-exec-bnb-smart-chain-hack-could-have-been-worse-if-validators-hadnt-sprung-into-action/>
Attacker exploited cryptographical logic to mint token infinitely.

But even when admin disallow a mode from further collaterize or disallow the lending pool from further collaterize, the hacker can donate the token to the lending pool and inflate the share worth to borrow all fund out.

  1. hacker transfers the infinitely minted token to the lending pool
  2. then hacker can call the [function flash](https://github.com/code-423n4/2023-12-initcapital/blob/a53e401529451b208095b3af11862984d0b32177/contracts/core/InitCore.sol#L383)

This would trigger the function syncCash, which update the cash amount in the lending pool to make sure the donated token count into the token worth
    
```solidity
    // execute callback
    IFlashReceiver(msg.sender).flashCallback(_pools, _amts, fees, _data);
    // sync cash
    for (uint i; i < _pools.length; i = i.uinc()) {
        uint poolCash = ILendingPool(_pools[i]).syncCash();
```

[Sync cash is called](https://github.com/code-423n4/2023-12-initcapital/blob/a53e401529451b208095b3af11862984d0b32177/contracts/lending_pool/LendingPool.sol#L148)
    
```solidity
    /// @inheritdoc ILendingPool
    function syncCash() external accrue onlyCore returns (uint newCash) {
        newCash = IERC20(underlyingToken).balanceOf(address(this));
        _require(newCash >= cash, Errors.INVALID_AMOUNT_TO_REPAY); // flash not repay
        cash = newCash;
    }
```

Basically by using the flash function and then trigger syncCash, user can always donate the token to the pool to inflate share worth.

Then in the collateral credit calculation, we are [converting shares worth to amount worth](https://github.com/code-423n4/2023-12-initcapital/blob/a53e401529451b208095b3af11862984d0b32177/contracts/core/InitCore.sol#L462)
    
```solidity
    uint tokenValue_e36 = ILendingPool(pools[i]).toAmtCurrent(shares[i]) * tokenPrice_e36;
```

Which calls the function [toAmt](https://github.com/code-423n4/2023-12-initcapital/blob/a53e401529451b208095b3af11862984d0b32177/contracts/lending_pool/LendingPool.sol#L266)
    
```solidity
    function _toAmt(uint _shares, uint _totalAssets, uint _totalShares) internal pure returns (uint amt) {
        return _shares.mulDiv(_totalAssets + VIRTUAL_ASSETS, _totalShares + VIRTUAL_SHARES);
    }
```

Assume shares do not change.  
Assume total shares does not change.

Clearly inflating the total asset (which is _cash + debt) inflates share worth.

Again, in the case of infinite token minting, hacker can donate the token to the lending pool to inflate the collateral credit and borrow all fund out and create large bad debt.

## Recommendation
Use internal balance to track the cash amount and do not allow user to indirectly access the sync cash function via flash loan.
