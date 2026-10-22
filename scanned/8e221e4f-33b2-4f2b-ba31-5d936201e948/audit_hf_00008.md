# [M] Inconsistent Dark Amount Calculation in getBurnableDarkLeft() and redeemBonds()

## Summary
Severity: Medium
Contest weight: 0.5918
Dataset id: 38
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Treasury contract, the getBurnableDarkLeft() viewer function allows the caller to get the _burnableDarkLeft. As shown in the following code snippets, the _burnableDarkLeft takes the minimum value between epochSupplyContractionLeft and _maxBurnableDark, where _maxBurnableDark is derived from _maxMintableBond.mul(_darkPrice).div(1e18) (line 189).
```solidity
function getBurnableDarkLeft() public view returns (uint256 _burnableDarkLeft) {
    uint256 _darkPrice = getDarkPrice();
    if (_darkPrice <= darkPriceOne) {
        uint256 _darkSupply = getDarkCirculatingSupply();
        uint256 _bondMaxSupply = _darkSupply.mul(maxDebtRatioPercent).div(10000);
        uint256 _bondSupply = IERC20(light).totalSupply();
        if (_bondMaxSupply > _bondSupply) {
            uint256 _maxMintableBond = _bondMaxSupply.sub(_bondSupply);
            uint256 _maxBurnableDark = _maxMintableBond.mul(_darkPrice).div(1e18);
            _burnableDarkLeft = Math.min(epochSupplyContractionLeft, _maxBurnableDark);
        }
    }
}
```
On the other hand, the redeemBonds() function in the same contract also calculates the amount of DARK could be redeemed. As shown in the following code snippets, the _darkAmount is derived from _bondAmount.mul(_rate).div(1e18) (line 466). The inconsistent Dark amount calculations between these two functions may introduce unexpected result.
```solidity
function redeemBonds(uint256 _bondAmount, uint256 targetPrice) external onlyOneBlock checkCondition checkOperator {
    require(_bondAmount > 0, "Treasury: cannot redeem bonds with zero amount");
    uint256 darkPrice = getDarkPrice();
    require(darkPrice == targetPrice, "Treasury: DARK price moved");
    require(
        darkPrice > darkPriceCeiling, // price > $1.01
        "Treasury: darkPrice not eligible for bond purchase"
    );
    uint256 _rate = getBondPremiumRate();
    require(_rate > 0, "Treasury: invalid bond rate");
    uint256 _darkAmount = _bondAmount.mul(_rate).div(1e18);
    require(IERC20(dark).balanceOf(address(this)) >= _darkAmount, "Treasury: treasury has no more budget");
    seigniorageSaved = seigniorageSaved.sub(Math.min(seigniorageSaved, _darkAmount));
    IBasisAsset(light).burnFrom(msg.sender, _bondAmount);
    IERC20(dark).safeTransfer(msg.sender, _darkAmount);
    _updateDarkPrice();
    emit RedeemedBonds(msg.sender, _darkAmount, _bondAmount);
}
```

## Recommendation
No data
