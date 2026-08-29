# [H] Anyone is able to redeem underlying asset from ERC5095 contract pre-maturity

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-illuminate
Published: 2022-11-10
Source: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/163
Type: sherlock-finding

## Details
cryptphi

high

# Anyone is able to redeem underlying asset from ERC5095 contract pre-maturity

## Summary
The current redeem logic of ERC5095.redeem() allows a token owner to be able to redeem without burning token before maturity

## Vulnerability Detail
The ERC5095.redeem() is meant to allow a token (ERC5095) owner or approved caller to redeem the asset of the underlying token pre-maturity or on/after maturity.

However the pre-maturity logic allows for redemption of underlying asset by anybody, owner or approved caller without any token burining and thereby having all risks borne by the contract thereby which leads to theft and loss of funds. This is due to the direct selling of principal token and transfer to receiver without the `_burn` call.

Additionally, it is for owner and an approved owner to collaborate and steal funds from the contract with this pre-maturity logic by calling ERC20Permit.permit() to set allowance before each redeem call pre-maturity.

## Impact
Loss of funds

## Code Snippet
Redeem Pre-maturity logic
https://github.com/sherlock-audit/2022-10-illuminate/blob/main/src/tokens/ERC5095.sol#L284-L319
```solidity
function redeem(
        uint256 s,
        address r,
        address o
    ) external override returns (uint256) {
        // Pre-maturity
        if (block.timestamp < maturity) {
            uint128 assets = Cast.u128(previewRedeem(s));
            // If owner is the sender, sell PT without allowance check
            if (o == msg.sender) {
                uint128 returned = IMarketPlace(marketplace).sellPrincipalToken(
                    underlying,
                    maturity,
                    Cast.u128(s),
                    assets - (assets / 100)
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/163_
