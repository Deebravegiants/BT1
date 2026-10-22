# [M] Improper Calculation of getBurnableDollarLeft()

## Summary
Severity: Medium
Contest weight: 0.4394
Dataset id: 12703
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Pegasus Dollar protocol, the PUSD token is the stable coin with the purpose of being used as a means of exchange. The protocol's built-in stability mechanism deterministically expands and contracts the PUSD supply to keep it pegged to one USDC token (which trades close to a single United States Dollar). While reviewing the Treasury contract, there is a public getter function that needs to be improved. To elaborate, we show below the related getBurnableDollarLeft() getter function. As the name indicates, this function is designed to calculate the burnable dollar left in Treasury. However, the current logic computes the burnable dollar with the spot price dollarPrice (line 1036). Our analysis shows it should be computed with the getBondDiscountRate() as follows: uint256 _maxBurnableDollar = _maxMintableBond.mul(1e18).div(getBondDiscountRate()).
```solidity
function getBurnableDollarLeft() public view returns (uint256 _burnableDollarLeft) {
    uint256 _dollarPrice = getDollarPrice();
    if (_dollarPrice <= dollarPriceOne) {
        uint256 _dollarSupply = getDollarCirculatingSupply();
        uint256 _bondMaxSupply = _dollarSupply.mul(maxDebtRatioPercent).div(10000);
        uint256 _bondSupply = IERC20(bond).totalSupply();
        if (_bondMaxSupply > _bondSupply) {
            uint256 _maxMintableBond = _bondMaxSupply.sub(_bondSupply);
            uint256 _maxBurnableDollar = _maxMintableBond.mul(_dollarPrice).div(1e18);
            _burnableDollarLeft = Math.min(epochSupplyContractionLeft, _maxBurnableDollar);
        }
    }
}
```

## Recommendation
Revise the above getBurnableDollarLeft() routine for the proper burnable dollar calculation. Result The issue has been fixed by this commit: 3ec3be0.
