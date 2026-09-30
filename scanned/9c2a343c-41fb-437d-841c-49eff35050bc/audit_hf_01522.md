# [M] Incorrect SURCHARGE multiplication

## Summary
Severity: Medium
Contest weight: 0.5684
Dataset id: 8042
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
In the _setAtlasLock() function, the following code sets claims to the maximum amount of ETH the bundler will use, including a surcharge:
// Set the claimed amount
uint256 rawClaims = (gasMarker + 1) * tx.gasprice;
claims = rawClaims + ((rawClaims * SURCHARGE) / 10_000_000);
Later on in the _settle() function, the remaining unused gas is subtracted from claims, also including the surcharge:
uint256 gasRemainder = (gasleft() * tx.gasprice);
gasRemainder += ((gasRemainder * SURCHARGE) / 10_000_000);
_claims -= gasRemainder;
Since both of these terms included the surcharge, the _claims value in _settle() ultimately represents the total ETH used by the bundler plus the surcharge amount. Therefore the following calculation is based on a combined amount, which is incorrect:
uint256 netGasSurcharge = (_claims * SURCHARGE) / 10_000_000;
_claims -= netGasSurcharge;
surcharge = _surcharge + netGasSurcharge;
SafeTransferLib.safeTransferETH(bundler, _claims);
```
For example, with a 10% surcharge, this code sets netGasSurcharge to 10% of 110% of the total ETH used, which leads to the bundler only being reimbursed 99% of the ETH they spent.

## Recommendation
Since _claims is already a combined value, the amount to multiply by the SURCHARGE should instead be _claims * 10_000_000 / (10_000_000 + SURCHARGE). In the netGasSurcharge calculation, this would be equivalent to making the following change:
```solidity
- uint256 netGasSurcharge = (_claims * SURCHARGE) / 10_000_000;
+ uint256 netGasSurcharge = (_claims * SURCHARGE) / (10_000_000 + SURCHARGE);
```
