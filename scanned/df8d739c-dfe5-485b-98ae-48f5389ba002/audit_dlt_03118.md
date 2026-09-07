# [H] Owner cannot withdraw all interest due to wrong calculation of accrued interest in WithdrwaCarry

## Summary
Severity: High
Chain: Smart contract
Component: 2023-11-canto
Published: 2023-11-17
Source: https://github.com/code-423n4/2023-11-canto-findings/issues/181
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-canto/blob/335930cd53cf9a137504a57f1215be52c6d67cb3/asD/src/asD.sol#L72-L90


# Vulnerability details

## Impact

The current `withdrawCarry` function in the contract underestimates the accrued interest due to a miscalculation. This error prevents the rightful owner from withdrawing their accrued interest, effectively locking the assets. The primary issue lies in the calculation of `maximumWithdrawable` within `withdrawCarry`.

### Flawed Calculation:

The following code segment is used to determine `maximumWithdrawable`:
```
uint256 exchangeRate = CTokenInterface(cNote).exchangeRateCurrent(); // Scaled by 1 * 10^(18 - 8 + Underlying Token Decimals), i.e. 10^(28) in our case
// The amount of cNOTE the contract has to hold (based on the current exchange rate which is always increasing) such that it is always possible to receive 1 NOTE when burning 1 asD
uint256 maximumWithdrawable = (CTokenInterface(cNote).balanceOf(address(this)) * exchangeRate) / 1e28 - totalSupply();
```
The problem arises with the scaling of `exchangeRate`, which is assumed to be scaled by `10^28`. However, for `CNOTE` in the Canto network, the `exchangeRate` is actually scaled by `10^18`. This discrepancy causes the owner to withdraw only 10^(-10) times the actual interest amount. Consequently, when a non-zero `_amount` is specified, `withdrawCarry` often fails due to the `require(_amount <= maximumWithdrawable, "Too many tokens requested");` condition.


## Proof of Concept

### CNOTE Scaling Verification

An essential aspect of this audit involves verifying the scaling factor of the `CNOTE` exchange rate. The `exchangeRate` scale for `CNOTE` can be verified in the [Canto Network's GitHub repository](https://github.com/Canto-Network/clm/blob/298377c8711a067a2a49d75a8bf2f90bbbe3de9e/src/CErc20.sol#L15).  Evidence confirming that the exponent of the `CNOTE` exchange rate is indeed `18` can be found through [this link to the token tracker](https://tuber.build/token/0xEe602429Ef7eCe0a13e4FfE8dBC16e101049504C?tab=read_proxy). The data provided there shows the current value of the stored exchange rate (exchangeRateStored) as approximately `1004161485744613000`. This value corresponds to `1.00416 * 1e18`, reaffirming the 10^18 scaling factor.

This information is critical for accurately understanding the mechanics of CNOTE and ensuring that the smart contract's calculations align with the actual scaling used in the token's implementation. The verification of this scaling factor supports the recommendations for adjusting the main contract's calculations and the associated test cases, as previously outlined.


### Testing with Solidity Codes

Testing with the following Solidity code illustrates the actual `CNOTE` values:
```solidity
function updateBalance() external {
    updatedUnderlyingBalance = ICNoteSimple(cnote).balanceOfUnderlying(msg.sender);
    updatedExchangeRate = ICNoteSimple(cnote).exchangeRateCurrent();
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-11-canto-findings/issues/181_
