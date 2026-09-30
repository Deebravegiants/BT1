# [M] lastFeeMintTime is updated even when streamingFee

## Summary
Severity: Medium
Contest weight: 0.5930
Dataset id: 22924
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
lastFeeMintTime is updated even when streamingFee is zero leading to manager fee losses. The function _availableManagerFee is used in calculating streamingFee. The fee depends majorly on _tokenSupply and timeChange

```solidity
// this timestamp for old pools would be zero at the first time
if (lastFeeMintTime != 0) {
    uint256 timeChange = block.timestamp.sub(lastFeeMintTime);
    uint256 streamingFee = _tokenSupply.mul(timeChange).mul(_managerFeeNumerator).div(_feeDenominator).div(365 days);
    available = available.add(streamingFee);
}
```

Let's say _tokenSupply = 200000, timeChange = 3600, _managerFeeNumerator = 300, _feeDenominator = 10000. The streaming fee will be 0. The issue is that in the _mintManagerFee function, the manager will not get minted any streaming fees but the lastFeeMintTime will be updated.

```solidity
function _mintManagerFee() internal returns (uint256 fundValue) {
    fundValue = IPoolManagerLogic(poolManagerLogic).totalFundValueMutable();
    uint256 tokenSupply = totalSupply();
    (uint256 performanceFeeNumerator, uint256 managerFeeNumerator, , uint256 managerFeeDenominator) = IPoolManagerLogic(
        poolManagerLogic
    ).getFee();
    uint256 available = _availableManagerFee(
        fundValue,
        tokenSupply,
        performanceFeeNumerator,
        managerFeeNumerator,
        managerFeeDenominator
    );
    address daoAddress = IHasDaoInfo(factory).daoAddress();
    uint256 daoFeeNumerator;
    uint256 daoFeeDenominator;
    (daoFeeNumerator, daoFeeDenominator) = IHasDaoInfo(factory).getDaoFee();
    uint256 daoFee = available.mul(daoFeeNumerator).div(daoFeeDenominator);
    uint256 managerFee = available.sub(daoFee);
    if (daoFee > 0) _mint(daoAddress, daoFee);
    if (managerFee > 0) _mint(manager(), managerFee);
    uint256 currentTokenPrice = _tokenPrice(fundValue, tokenSupply);
    if (tokenPriceAtLastFeeMint < currentTokenPrice) {
        tokenPriceAtLastFeeMint = currentTokenPrice;
    }
    lastFeeMintTime = block.timestamp;
}
```

In effect the manager will get 0 fees for that one hour that has passed because the next time the function is called that hour will not be taken into account due to the update of lastFeeMintTime. Loss of manager fees.

## Recommendation
Only update the lastFeeMintTime to block.timestamp if streamingFee is greater than
