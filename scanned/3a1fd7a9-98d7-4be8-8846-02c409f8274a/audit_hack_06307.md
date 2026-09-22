# [M] The contract Vault may revert on `claim` if there is not enough WETH to transfer to the owner of the NFT tokenid

## Summary
Severity: Medium
Reporter: weeeh_
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L459
Type: audit-issue

## Details
# The contract Vault may revert on `claim` if there is not enough WETH to transfer to the owner of the NFT tokenid

## Summary
If the contract Vault runs out of WETH, for some reasons, and a NFT owner wants to claim his share of pending WETH, then the function will revert causing a denial of service.

## Vulnerability Detail
When a NFT owner claims his share of pending WETH by calling `Vault.claim(_token_id)`, and the amount to claim is greater than the WETH balance of Vault contract, then the function will revert on `ERC20(WETH).transfer(token_owner, amount)` call, and so possibly causing a denial of service.

## Impact
NFT owners are not able to receive their amount of share and no event is generated on Vault side.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L459

## Tool used
vim
Manual Review

## Recommendation
Before calling `ERC20(WETH).transfer` the contract should check the balance. If not enough amount are available then an event should be emitted.
