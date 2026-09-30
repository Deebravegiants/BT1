# [M] Unexpected behavior when calling certain ERC4626

## Summary
Severity: Medium
Contest weight: 0.5947
Dataset id: 22398
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Unexpected behavior could occur when certain ERC4626 functions are called during the time windows when the fCash has matured but is not yet settled.
When the fCash has matured, the global settlement does not automatically get executed. The global settlement will only be executed when the first account attempts to settle its own account. The code expects the pr.supplyFactor to return zero if the global settlement has not been executed yet after maturity. that it expects that if fCash has matured AND the fCash has not yet been settled, the pr.supplyFactor will be zero. In this case, the cash value will be zero.
-fcash/contracts/wfCashBase.sol#L215
File: wfCashBase.sol
209:
```solidity
function _getMaturedCashValue(uint256 fCashAmount) internal view returns (uint256) {
    if (!hasMatured()) return 0;
    // If the fCash has matured we use the cash balance instead.
    (uint16 currencyId, uint40 maturity) = getDecodedID();
    PrimeRate memory pr = NotionalV2.getSettlementRate(currencyId, maturity);
    // fCash has not yet been settled
    if (pr.supplyFactor == 0) return 0;
}
```
During the time window where the fCash has matured, and none of the accounts triggered an account settlement, the _getMaturedCashValue function at Line 33 below will return zero, which will result in the totalAssets() function returning zero.
-fcash/contracts/wfCashERC4626.sol#L33
File: wfCashERC4626.sol
29:
```solidity
function totalAssets() public view override returns (uint256) {
    if (hasMatured()) {
        // We calculate the matured cash value of the total supply of fCash. This is
        // not always equal to the cash balance held by the wrapper contract.
        uint256 primeCashValue = _getMaturedCashValue(totalSupply());
        require(primeCashValue < uint256(type(int256).max));
        int256 externalValue = NotionalV2.convertCashBalanceToExternal(
            getCurrencyId(), int256(primeCashValue), true
        );
        return externalValue >= 0 ? uint256(externalValue) : 0;
    }
}
```
The totalAssets() function is utilized by key ERC4626 functions within the wrapper, such as the following functions. The side effects of this issue are documented below:
• convertToAssets (Impact = returned value is always zero assets regardless of the inputs)
• convertToAssets > previewRedeem (Impact = returned value is always zero assets regardless of the inputs)
• convertToAssets > previewRedeem > maxWithdraw (Impact = max withdrawal is always zero)
• convertToShares (Impact = Division by zero error, Revert)
• convertToShares > previewWithdraw (Impact = Revert)
In addition, any external protocol integrating with wfCash will be vulnerable within this time window as an invalid result (zero) is returned, or a revert might occur. For instance, any external protocol that relies on any of the above-affected functions for computing the withdrawal/minting amount or collateral value will be greatly impacted as the value before the maturity might be 10000, but it will temporarily reset to zero during this time window. Attackers could take advantage of this time window to perform malicious actions.

## Recommendation
Document the unexpected behavior of the affected functions that could occur during the time windows when the fCash has matured but is not yet settled so that anyone who calls these functions is aware of them.
