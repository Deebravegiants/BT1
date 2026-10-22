# [M] Possible Unintended Uses Of Exchange Unit

## Summary
Severity: Medium
Contest weight: 0.4464
Dataset id: 11615
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Amy protocol, supplying users may deposit their assets into the pool and get corresponding FToken in return. As an interest-bearing token, the FToken here plays exactly the same role as cToken in Compound or aToken in Aave. When examining the FToken logic, we notice the implicit requirement of FToken decimal that needs to be fixed (otherwise the exchange unit uses for the account health check may be abused for unintended purposes). And the decimal plays a critical role to normalize the FToken price and the associated value.
```solidity
function initFToken(
    uint256 _initialExchangeRate,
    address _controller,
    address _initialInterestRateModel,
    address _underlying,
    uint256 _borrowSafeRatio,
    string memory _name,
    string memory _symbol,
    uint8 _decimals,
    address _arbSys
) internal {
    initialExchangeRate = _initialExchangeRate;
    controller = IBankController(_controller);
    interestRateModel = IInterestRateModel(_initialInterestRateModel);
    admin = msg.sender;
    underlying = _underlying;
    borrowSafeRatio = _borrowSafeRatio;
    arbSys = _arbSys;
    accrualBlockNumber = getBlockNumber();
    borrowIndex = ONE;
    name = _name;
    symbol = _symbol;
    decimals = _decimals;
    _notEntered = true;
    securityFactor = 3000;
}
```
Speciﬁcally, the implicit assumption is that all FTokens should have the same 18 decimals. However, current initialization routine (as shown above) indicates that this decimal can be passed in as an argument. In other words, it depends on the external oﬀ-chain procedure to properly enforce this assumption. Note that a non-18 FToken decimal may lead to unexpected results when there is a need to compute or normalize the asset value.

## Recommendation
Enforce the implicit assumption by ensuring the given decimal is always 18.
