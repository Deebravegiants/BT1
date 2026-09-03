# [H] An attacker can control the calculation of `LEther::depositEth()`

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-sentiment
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-11-sentiment-judging/issues/10
Type: sherlock-finding

## Details
8olidity

high

# An attacker can control the calculation of `LEther::depositEth()`

## Summary
An attacker can control the calculation of `LEther::depositEth()`
## Vulnerability Detail
In `depositEth()`, `shares` are counted based on the number of `assets` passed in by the user,
```solidity
    function depositEth() external payable returns (uint shares) {
        uint assets = msg.value;

        beforeDeposit(assets, shares);
        if ((shares = previewDeposit(assets)) == 0) revert Errors.ZeroShares();

        IWETH(address(asset)).deposit{value: assets}();

        _mint(msg.sender, shares);
        emit Deposit(msg.sender, msg.sender, assets, shares);
    }
```
The result of `shares` is calculated by `previewDeposit()`

```solidity
    function previewDeposit(uint256 assets) public view virtual returns (uint256) {
        return convertToShares(assets);
    }

    function convertToShares(uint256 assets) public view virtual returns (uint256) {
        uint256 supply = totalSupply; // Saves an extra SLOAD if totalSupply is non-zero.

        return supply == 0 ? assets : assets.mulDivDown(supply, totalAssets());
    }
```
As you can see, the actual `shares` are counted by both `supply` and `totalassets()`, while `totalassets()` are counted by the `assets` of the contract, so an attacker could send `asset tokens` to the contract to manipulate the result of `convertToShares()`


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-sentiment-judging/issues/10_
