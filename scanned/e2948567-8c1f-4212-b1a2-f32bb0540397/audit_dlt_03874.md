# [M] `wfCashERC4626` - Lending at 0% interest with a fee-on-transfer asset makes vault insolvent

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-12-notional-update-5
Published: 2024-01-18
Source: https://github.com/sherlock-audit/2023-12-notional-update-5-judging/issues/58
Type: sherlock-finding

## Details
eol

high

# `wfCashERC4626` - Lending at 0% interest with a fee-on-transfer asset makes vault insolvent

## Summary
The `wfCash` vault is credited less prime cash than the `wfCash` it mints to the depositor when its underlying asset is a fee-on-transfer token. This leads to the vault being insolvent because it has issued more shares than can be redeemed. 

## Vulnerability Detail
When minting `wfCash` shares more than the `maxFCash` available, the `wfCashERC4626` vault lends the deposited assets at 0% interest. The assets are deposited by the vault into Notional and the depositor gets 1:1 `wfCash` in return. This works fine for assets that are not fee-on-transfer tokens. 
https://github.com/sherlock-audit/2023-12-notional-update-5/blob/main/wrapped-fcash/contracts/wfCashLogic.sol#L60-L68
```solidity
    if (maxFCash < fCashAmount) {
        // NOTE: lending at zero
        uint256 fCashAmountExternal = fCashAmount * precision / uint256(Constants.INTERNAL_TOKEN_PRECISION);
        require(fCashAmountExternal <= depositAmountExternal);

        // NOTE: Residual (depositAmountExternal - fCashAmountExternal) will be transferred
        // back to the account
        NotionalV2.depositUnderlyingToken{value: msgValue}(address(this), currencyId, fCashAmountExternal);
    } else if (isETH || hasTransferFee || getCashBalance() > 0) {
```
For fee-on-transfer tokens, the vault is credited prime cash based on the actual amount it received, which is `deposit amount - transfer fee`. 
https://github.com/sherlock-audit/2023-12-notional-update-5/blob/main/contracts-v3/contracts/internal/balances/TokenHandler.sol#L204-L214
```solidity
        } else {
            // In the case of deposits, we use a balance before and after check
            // to ensure that we record the proper balance change.
            actualTransferExternal = GenericToken.safeTransferIn(
                underlying.tokenAddress, account, underlyingExternalDeposit
            ).toInt();
        }

        netPrimeSupplyChange = _postTransferPrimeCashUpdate(
            account, currencyId, actualTransferExternal, underlying, primeRate
        );
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2023-12-notional-update-5-judging/issues/58_
