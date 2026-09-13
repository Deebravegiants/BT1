# [M] StaticATokenLM transfer missing _updateRewards

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-reserve
Published: 2023-08-03
Source: https://github.com/code-423n4/2023-07-reserve-findings/issues/12
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/e3d2681503499e81915797c77eeef8210352a138/contracts/plugins/assets/aave/StaticATokenLM.sol#L359


# Vulnerability details

## Impact
transfer missing `_updateRewards()`,Resulting in the loss of `from`'s reward

## Proof of Concept
`StaticATokenLM` contains the rewards mechanism, when the balance changes, the global `_accRewardsPerToken` needs to be updated first to calculate the user's `rewardsAccrued` more accurately.

Example: `mint()/burn()` both call `_updateRewards()` to update `_accRewardsPerToken`

```solidity
    function _deposit(
        address depositor,
        address recipient,
        uint256 amount,
        uint16 referralCode,
        bool fromUnderlying
    ) internal returns (uint256) {
        require(recipient != address(0), StaticATokenErrors.INVALID_RECIPIENT);
@>      _updateRewards();

...

        _mint(recipient, amountToMint);

        return amountToMint;
    }


    function _withdraw(
        address owner,
        address recipient,
        uint256 staticAmount,
        uint256 dynamicAmount,
        bool toUnderlying
    ) internal returns (uint256, uint256) {
...
@>      _updateRewards();

...
@>      _burn(owner, amountToBurn);

...
    }        
```

When `transfer()/transerFrom()`, the balance is also modified, but without calling `_updateRewards()` first
The result is that if the user transfers the balance, the difference in rewards accrued by `from` is transferred to `to` along with it.
This doesn't make sense for `from`.
```solidity
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256
    ) internal override {
        if (address(INCENTIVES_CONTROLLER) == address(0)) {
            return;
        }
        if (from != address(0)) {
            _updateUser(from);
        }
        if (to != address(0)) {
            _updateUser(to);
        }
    }
```
## Tools Used

## Recommended Mitigation Steps


`_beforeTokenTransfer` first trigger `_updateRewards()`
```solidity
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256
    ) internal override {
        if (address(INCENTIVES_CONTROLLER) == address(0)) {
            return;
        }
+       _updateRewards();        
        if (from != address(0)) {
            _updateUser(from);
        }
        if (to != address(0)) {
            _updateUser(to);
        }
    }
```


## Assessed type

Context
