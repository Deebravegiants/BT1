# [H] Mismatch in `withdraw`

## Summary
Severity: High
Contest weight: 0.6218
Dataset id: 15631
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As defined in the docs for Euler, ERC4626, Compound and Aave, when withdrawing and depositing funds the `amount` specified corresponds excactly to how many of the underlying assets are deposited or withdrawn.

However, as specified by [Yearn](https://docs.yearn.finance/vaults/smart-contracts/vault#withdraw), the yearn withdraw `amount` parameter specifies how many `shares` are burnt instead of underlying assets retrieved. Two scenarios can occur from then on, if there are not enough shares then the transaction will revert and users will not be able to redeem the underlying assets from Yearn. If there are enough shares, then a higher number of assets will be withdrawn then expected (as assets per share will only increase). This means that once the user receives their underlying assets at a 1:1 peg the excess amounts will be permanently locked in the vault contract.

## Proof of Concept
All scenarios use Yearn finance as the protocol, the other protocols are unaffected.

## Recommendation
In the `withdraw()` function in Swivel.sol, calculating the price per share and use that to retrieve the correct number of underlying assets e.g.

```solidity
uint256 pricePerShare = IYearnVault(c).pricePerShare();
return IYearnVault(c).withdraw(a / pricePerShare) >= 0;
```

Duplicate of [#30](https://github.com/code-423n4/2022-07-swivel-findings/issues/30).

I do not understand how this is a duplicate of #30, [#30](https://github.com/code-423n4/2022-07-swivel-findings/issues/30) talks about a problem with `redeemUnderlying()` in Compound while this issue talks about a problem with `withdraw()` when using yearn.

They both cannot be true at once however. Either the lib expects shares, or the lib expects assets. His suggestion notes inconsistency and recommends changing the compound redeem to align with yearn, while you note the inconsistency and recommend fixing the yearn math. At the end of the day the issue is the “mismatch”.

Fair enough, that makes sense. I would still disagree with their interpretation of the issue, it is clear from the code that `a` represents the underlying assets. If `a` does represent the number of shares then other functions such as `authRedeemzcTokens` would be plain wrong because it would be redeeming each zcToken as if it was one share not one underlying asset.

Yeah I actually kind of agree with you. We intended the implementation to align more with your finding.

That said it _might_ be worth a judge’s input.

If they think they’re different, the other finding is invalid/should be disputed and this one is correct.

Confirmed, good issue and marked [#30](https://github.com/code-423n4/2022-07-swivel-findings/issues/30) as a duplicate.

**[robrobbins (Swivel) resolved](https://github.com/code-423n4/2022-07-swivel-findings/issues/43#issuecomment-1234639671):**

Addressed: <https://github.com/Swivel-Finance/gost/pull/437>.
