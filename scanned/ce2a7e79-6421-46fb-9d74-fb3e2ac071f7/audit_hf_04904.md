# [H] mustUseContractFunds restrictions can be skipped due to check-before-set

## Summary
Severity: High
Contest weight: 0.8005
Dataset id: 22820
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
in takeTokensAndTrade() Checking useContractFund before setting mustUseContractFunds causing for the current loop swapOps[i].useContractFund to be unrestricted in takeTokensAndTrade() We restrict by mustUseContractFunds: after the first first split ops, all subsequent ops[] can only ops[x].useContractFunds==true
```solidity
function takeTokensAndTrade(
...
for (uint256 i = 0; i < swapOps.length; i++) {
    OperationParameters memory op = swapOps[i];
    require(mustUseContractFunds? op.useContractFunds : true, "Maradona: must use contract funds");
    bool isFromEthSwap = op.inputToken == address(0);
    uint256 ratioBPs = op.ratioBPs;
    require(ratioBPs > 0, "Maradona: ratioBPs must be greater than 0");
    require(ratioBPs <= 10000, "Maradona: ratioBPs must be less than or equal to 10000");
    // Check if last start address is different that the current start address
    // If it is, we reset the cumRatio and cumOutputAmount
    if (i > 0 && op.inputToken != lastAddress) {
        require(cumRatio == 10000, "Maradona: cumRatio is not 10000");
        cumRatio = 0;
        prevCumOutputAmount = cumOutputAmount;
        cumOutputAmount = 0;
        canBeFromEth = false;
        mustUseContractFunds = true;
    }
    require(markets[op.exchangeID] != address(0), "Maradona: market not registered");
    ISwapMarket market = ISwapMarket(markets[op.exchangeID]);
```
From the code above, we know that require(mustUseContractFunds? op.useContractFunds : true, “Maradona: must use contract funds”); This check is performed before setting mustUseContractFunds = true;. This way the current loop ops[i] is not restricted Example: ops[0] = {inputToken = eth } ops[1] = {inputToken = eth } ops[2] = {inputToken = usdc, useContractFunds =false} //«----success, this loop will set mustUseContractFunds==true, but useContractFunds can false because check before set Without the mustUseContractFunds restriction, there's no guarantee that all subsequent uses will be preceded by prevCumOutputAmount. Another possibility, which a malicious user can use to avoid the fees For example passing in ops[0] = {inputToken = eth , amountIn = 2} ops[1] = {inputToken = eth, useContractFunds=true} ops[2] = {inputToken = eth, useContractFunds =false} The number of eths used to count fees gets small

## Recommendation
```solidity
function takeTokensAndTrade(
...
for (uint256 i = 0; i < swapOps.length; i++) {
    OperationParameters memory op = swapOps[i];
    bool isFromEthSwap = op.inputToken == address(0);
    uint256 ratioBPs = op.ratioBPs;
    require(ratioBPs > 0, "Maradona: ratioBPs must be greater than 0");
    require(ratioBPs <= 10000, "Maradona: ratioBPs must be less than or equal to 10000");
    // Check if last start address is different that the current start address
    // If it is, we reset the cumRatio and cumOutputAmount
    if (i > 0 && op.inputToken != lastAddress) {
        require(cumRatio == 10000, "Maradona: cumRatio is not 10000");
        cumRatio = 0;
        prevCumOutputAmount = cumOutputAmount;
        cumOutputAmount = 0;
        canBeFromEth = false;
        mustUseContractFunds = true;
    }
    require(mustUseContractFunds? op.useContractFunds : true, "Maradona: must use contract funds");
    require(markets[op.exchangeID] != address(0), "Maradona: market not registered");
    ISwapMarket market = ISwapMarket(markets[op.exchangeID]);
```
