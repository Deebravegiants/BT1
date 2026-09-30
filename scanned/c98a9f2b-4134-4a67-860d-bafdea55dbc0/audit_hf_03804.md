# [H] Unable to transfer fee reserve assets to trea-

## Summary
Severity: High
Contest weight: 0.7578
Dataset id: 20018
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Transferring fee reserve assets to the treasury manager contract will result in a revert.

```solidity
/// @notice redeems and transfers tokens to the treasury manager contract
function _redeemAndTransfer(uint16 currencyId, int256 primeCashRedeemAmount) private returns (uint256) {
    PrimeRate memory primeRate = PrimeRateLib.buildPrimeRateStateful(currencyId);
    int256 actualTransferExternal = TokenHandler.withdrawPrimeCash(
        treasuryManagerContract,
        currencyId,
        primeCashRedeemAmount.neg(),
        primeRate,
        true // if ETH, transfers it as WETH
    );

    require(actualTransferExternal > 0);
    return uint256(actualTransferExternal);
}
```

The value returned by the TokenHandler.withdrawPrimeCash function is always less than or equal to zero. Thus, the condition actualTransferExternal > 0 will always be false, and the _redeemAndTransfer function will always revert.

The transferReserveToTreasury function depends on _redeemAndTransfer function. Thus, it is not possible to transfer any asset to the treasury manager contract. The fee collected by Notional is stored in the Fee Reserve. The fee reserve assets are unable to be moved.

## Recommendation
Negate the value returned by the TokenHandler.withdrawPrimeCash function.

```solidity
int256 actualTransferExternal = TokenHandler.withdrawPrimeCash(
    treasuryManagerContract,
    currencyId,
    primeCashRedeemAmount.neg(),
    primeRate,
    true // if ETH, transfers it as WETH
).neg();
```
