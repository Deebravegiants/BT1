# [H] _settleCurrency does not properly interact with the poolManager when calling settle

## Summary
Severity: High
Contest weight: 0.7730
Dataset id: 4149
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function _settleCurrency(Currency currency) internal {
    int256 amount = poolManager.currencyDelta(address(this), currency);
    if (amount < 0) {
        // address(this) owes PoolManager currency
        // contract already has input tokens in its balance
        // so we directly transfer tokens to PoolManager
        uint256 absAmount = uint256(-amount);
        if (currency.isNative()) {
            // native currency (e.g. ETH)
            poolManager.settle{value: absAmount}();
        } else {
            // ERC20 token
            poolManager.sync(currency);
            currency.transfer(address(poolManager), absAmount);
            // @audit - should use poolManager.settle()
            IPoolManagerOld(address(poolManager)).settle
            //(currency); // TODO: compatible with old sepolia v4 deploy, use pool
        } else if (amount > 0) {
            // address(this) has positive balance in PoolManager
            // take tokens from PoolManager to address(this)
            // the reactor will use transferFrom() to take tokens from address
            //(this)
            poolManager.take(currency, address(this), uint256(amount));
```

## Recommendation
```solidity
function _settleCurrency(Currency currency) internal {
    int256 amount = poolManager.currencyDelta(address(this), currency);
    if (amount < 0) {
        // address(this) owes PoolManager currency
        // contract already has input tokens in its balance
        // so we directly transfer tokens to PoolManager
        uint256 absAmount = uint256(-amount);
        if (currency.isNative()) {
            // native currency (e.g. ETH)
            poolManager.settle{value: absAmount}();
        } else {
            // ERC20 token
            poolManager.sync(currency);
            currency.transfer(address(poolManager), absAmount);
            // @audit - should use poolManager.settle()
            // IPoolManagerOld(address(poolManager)).settle
            // (currency); // TODO: compatible with old sepolia v4 deploy, use poolManager.settle()
            poolManager.settle();
        } else if (amount > 0) {
            // address(this) has positive balance in PoolManager
            // take tokens from PoolManager to address(this)
            // the reactor will use transferFrom() to take tokens from address
            //(this)
            poolManager.take(currency, address(this), uint256(amount));
```
