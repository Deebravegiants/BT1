# [M] Improper Logic in BaseToUsdAssimilator::outputRaw()

## Summary
Severity: Medium
Contest weight: 0.4232
Dataset id: 13435
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Xave protocol supports a number of built-in assimilators, which allow for the conversion among related assets. For example, both BaseToUsdAssimilator and UsdcToUsdAssimilator have defined a function outputRaw(), which takes a raw amount of USDC/baseToken and transfers it out with the numeraire value of the raw amount. Our analysis shows this function needs to be revised.

To elaborate, we use the BaseToUsdAssimilator contract as an example and show below the outputRaw() implementation. While it is designed to return the numeraire value of the given output raw amount, the actual amount for the transfer() call should be the given _amount, not the computed numeraire amount: baseToken.transfer(_dst, _baseTokenAmount) (line 145). Note the same issue is applicable to the same outputRaw() function in the UsdcToUsdAssimilator contract.

```solidity
function outputRaw(address _dst, uint256 _amount)
    external
    override
    returns (int128 amount_)
{
    uint256 _rate = getRate();
    uint256 _baseTokenAmount = (_amount * _rate) / 1e8;
    bool _transferSuccess = baseToken.transfer(_dst, _baseTokenAmount);
    require(_transferSuccess, "BaseAssimilator/baseToken-transfer-failed");
    amount_ = _baseTokenAmount.divu(baseDecimals);
}
```

## Recommendation
Revise the above outputRaw() function in the two contracts BaseToUsdAssimilator and UsdcToUsdAssimilator to use the right amount for the transfer() call.
