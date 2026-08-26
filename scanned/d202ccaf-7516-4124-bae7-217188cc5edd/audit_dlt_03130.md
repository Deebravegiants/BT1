# [M] Permit doesnt work with DAI

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-03-pooltogether
Published: 2024-03-07
Source: https://github.com/code-423n4/2024-03-pooltogether-findings/issues/51
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-03-pooltogether/blob/480d58b9e8611c13587f28811864aea138a0021a/pt-v5-vault/src/PrizeVault.sol#L524-L546


# Vulnerability details

## Impact

The function `depositWithPermit` in `PrizeVault.sol` contract is used with permit options so that users can submit a signed message and use that to give allowance to the contract to then extract the tokens required for the deposit.

```solidity
IERC20Permit(address(_asset)).permit(_owner, address(this), _assets, _deadline, _v, _r, _s);
```

The issue is that the test suite shows that the protocol aims to use sDAI, the dai savings rate, but the DAI token's permit signature is different. From the contract at address `0x6B175474E89094C44Da98b954EedeAC495271d0F`, we see the `permit` function

```solidity
function permit(address holder, address spender, uint256 nonce, uint256 expiry,
                    bool allowed, uint8 v, bytes32 r, bytes32 s) external
```

Due to the missing `nonce` field, DAI, a token which allows permit based interactions, cannot be used with signed messages for depositing into sDAI vaults. Due to the wrong parameters, the permit transactions will revert.


## Proof of Concept

It is evident from the code that the permit function call does not match the signature of DAI's permit function.

## Tools Used

Manual Review

## Recommended Mitigation Steps

For the special case of DAI token, allow a different implementation of the permit function which allows a nonce variable.



_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-03-pooltogether-findings/issues/51_
