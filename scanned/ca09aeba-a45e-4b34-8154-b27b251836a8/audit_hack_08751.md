# [H] No privilege control in CollateralManager.setCollateralEscrowBeacon

## Summary
Severity: High
Reporter: evilakela
Source: https://github.com/sherlock-audit/2023-03-teller/blob/main/teller-protocol-v2/packages/contracts/contracts/CollateralManager.sol#L91-L96
Type: audit-issue

## Details
# No privilege control in CollateralManager.setCollateralEscrowBeacon

## Summary
No privilege control in `CollateralManager.setCollateralEscrowBeacon`

## Vulnerability Detail

## Impact
Anyone can call this function, set it's own `collateralEscrowBeacon` and essentially break protocol

## Code Snippet
https://github.com/sherlock-audit/2023-03-teller/blob/main/teller-protocol-v2/packages/contracts/contracts/CollateralManager.sol#L91-L96

## Tool used
Manual Review

## Recommendation
Add onlyOwner modifier
